import os
import sys
import logging
import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import signal
import threading
import time

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s | %(levelname)-8s | %(name)-12s | %(funcName)-15s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.FileHandler(log_dir / 'scraper.log', encoding='utf-8')  # File output
        ]
    )
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Add scraper folder to Python path (cross-platform)
current_dir = Path(__file__).parent
scraper_dir = current_dir / 'scraper'
sys.path.insert(0, str(scraper_dir))

# Initialize FastAPI app
app = FastAPI(
    title="Web Scraper API",
    description="Production-ready web scraper with phase-based execution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state management
class ScraperState:
    def __init__(self):
        self.status: Dict[str, Dict[str, Any]] = {
            "phase1": {
                "running": False,
                "last_run": None,
                "last_status": "not_started",
                "last_error": None,
                "run_count": 0
            },
            "phase2": {
                "running": False,
                "last_run": None,
                "last_status": "not_started",
                "last_error": None,
                "run_count": 0
            }
        }
        self.app_started = datetime.now(timezone.utc).isoformat()
        self.total_runs = 0
        self._lock = threading.Lock()
    
    def update_status(self, phase: str, **kwargs):
        with self._lock:
            self.status[phase].update(kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "app_started": self.app_started,
                "total_runs": self.total_runs,
                "phases": self.status.copy(),
                "server_time": datetime.now(timezone.utc).isoformat()
            }

# Initialize global state
scraper_state = ScraperState()

# Import scrapers with error handling
def import_scrapers():
    """Dynamically import scraper modules with error handling"""
    scrapers = {}
    
    try:
        # Try to import category_scraper
        from scraper import category_scraper
        scrapers['phase1'] = getattr(category_scraper, 'main', None)
        logger.info("Successfully imported category_scraper")
    except ImportError as e:
        logger.error(f"Failed to import category_scraper: {e}")
        scrapers['phase1'] = None
    
    try:
        # Try to import new_scraper2
        from scraper import new_scraper2
        scrapers['phase2'] = getattr(new_scraper2, 'main', None)
        logger.info("Successfully imported new_scraper2")
    except ImportError as e:
        logger.error(f"Failed to import new_scraper2: {e}")
        scrapers['phase2'] = None
    
    return scrapers

# Load scrapers
SCRAPERS = import_scrapers()

# Health check endpoint
@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    return {
        "status": "healthy",
        "service": "Web Scraper API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scrapers_available": {
            "phase1": SCRAPERS['phase1'] is not None,
            "phase2": SCRAPERS['phase2'] is not None
        }
    }

# Status endpoint
@app.get("/status", tags=["Monitoring"])
async def get_scraper_status():
    """Get detailed scraper status"""
    return scraper_state.get_status()

# Scraper execution functions
async def execute_scraper(phase: str, scraper_func) -> Dict[str, Any]:
    """Execute a scraper function with comprehensive error handling"""
    if scraper_func is None:
        raise HTTPException(status_code=404, detail=f"Scraper for {phase} not found")
    
    if scraper_state.status[phase]["running"]:
        raise HTTPException(status_code=409, detail=f"{phase} scraper is already running")
    
    # Update status to running
    scraper_state.update_status(
        phase,
        running=True,
        last_status="running",
        last_error=None
    )
    
    start_time = time.time()
    logger.info(f"Starting {phase} scraper execution")
    
    try:
        # Run scraper in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, scraper_func)
        
        execution_time = time.time() - start_time
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Update success status
        scraper_state.update_status(
            phase,
            running=False,
            last_run=timestamp,
            last_status="completed",
            run_count=scraper_state.status[phase]["run_count"] + 1
        )
        scraper_state.total_runs += 1
        
        logger.info(f"{phase} scraper completed successfully in {execution_time:.2f} seconds")
        
        return {
            "status": "completed",
            "execution_time": round(execution_time, 2),
            "timestamp": timestamp,
            "phase": phase
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        timestamp = datetime.now(timezone.utc).isoformat()
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # Update error status
        scraper_state.update_status(
            phase,
            running=False,
            last_run=timestamp,
            last_status="error",
            last_error=error_msg
        )
        
        logger.error(f"{phase} scraper failed after {execution_time:.2f} seconds: {error_msg}")
        logger.debug(f"Full traceback: {error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": error_msg,
                "phase": phase,
                "execution_time": round(execution_time, 2),
                "timestamp": timestamp
            }
        )
    
    finally:
        # Ensure running status is reset
        scraper_state.update_status(phase, running=False)

# API endpoints for scraper execution
@app.post("/scrape/phase1", tags=["Scrapers"])
async def run_phase1():
    """Execute Phase 1: Category Scraper"""
    result = await execute_scraper("phase1", SCRAPERS['phase1'])
    return result

@app.post("/scrape/phase2", tags=["Scrapers"])
async def run_phase2():
    """Execute Phase 2: New Scraper"""
    result = await execute_scraper("phase2", SCRAPERS['phase2'])
    return result

@app.post("/scrape/both", tags=["Scrapers"])
async def run_both_phases():
    """Execute both scrapers sequentially"""
    if any(scraper_state.status[phase]["running"] for phase in ["phase1", "phase2"]):
        raise HTTPException(status_code=409, detail="One or more scrapers are already running")
    
    logger.info("Starting sequential execution of both scrapers")
    results = []
    
    try:
        # Execute Phase 1
        result1 = await execute_scraper("phase1", SCRAPERS['phase1'])
        results.append(result1)
        
        # Execute Phase 2
        result2 = await execute_scraper("phase2", SCRAPERS['phase2'])
        results.append(result2)
        
        logger.info("Both scrapers completed successfully")
        return {
            "status": "completed",
            "message": "Both scrapers executed successfully",
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException as e:
        logger.error(f"Failed during sequential execution: {e.detail}")
        raise e

# Stop scrapers endpoint (for emergency stops)
@app.post("/scrape/stop", tags=["Control"])
async def stop_scrapers():
    """Emergency stop for all scrapers (note: may not work for all scraper types)"""
    logger.warning("Emergency stop requested")
    # This is a placeholder - actual implementation depends on scraper architecture
    return {
        "message": "Stop signal sent (effectiveness depends on scraper implementation)",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Graceful shutdown handling
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    
    # Check if any scrapers are running
    if any(scraper_state.status[phase]["running"] for phase in ["phase1", "phase2"]):
        logger.warning("Scrapers are still running during shutdown")
    
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Web Scraper API starting up...")
    logger.info(f"Available scrapers: {list(k for k, v in SCRAPERS.items() if v is not None)}")
    logger.info("API documentation available at /docs")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Web Scraper API shutting down...")

# Main application entry point
if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 80))  # Default to 80 for tiangolo image
    workers = int(os.getenv("WORKERS", 1))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Workers: {workers}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        access_log=True,
        reload=False  # Disable reload in production
    )

# For tiangolo/uvicorn-gunicorn-fastapi base image
# The base image will automatically discover and run the FastAPI app
# No need for explicit uvicorn.run() when using the base image