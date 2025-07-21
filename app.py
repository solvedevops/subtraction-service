from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import uuid
from telemetry import create_telemetry_logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize telemetry
telemetry = create_telemetry_logger("subtraction-service")
logger = telemetry.get_logger()

# Response model for API documentation
class SubtractionResult(BaseModel):
    result: float
    operation: str = "subtraction"
    first_number: float
    second_number: float

class HealthCheck(BaseModel):
    status: str
    service: str

def subtraction(firstNumber: float, secondNumber: float) -> float:
    """Perform subtraction of two numbers."""
    # Start trace
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        result = firstNumber - secondNumber
        duration_ms = (time.time() - start_time) * 1000
        
        # Log successful operation
        logger.info(f"Subtraction performed: {firstNumber} - {secondNumber} = {result}")
        
        # Log trace
        telemetry.log_trace(
            trace_id=trace_id,
            span_id=span_id,
            operation="subtraction",
            duration_ms=duration_ms,
            metadata={
                "first_number": firstNumber,
                "second_number": secondNumber,
                "result": result
            }
        )
        
        # Log metrics
        telemetry.log_metrics({
            "operation": "subtraction",
            "success": True,
            "response_time_ms": duration_ms
        })
        
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        telemetry.log_error_with_trace(e, {
            "operation": "subtraction",
            "first_number": firstNumber,
            "second_number": secondNumber,
            "duration_ms": duration_ms
        })
        raise


app = FastAPI(
    title="Subtraction Service",
    description="Microservice for performing subtraction operations",
    version="1.0.0"
)
FastAPIInstrumentor().instrument_app(app)
@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint to verify service is running."""
    logger.info("Health check requested")
    telemetry.log_metrics({
        "health_check": 1,
        "service": "subtraction-service",
        "status": "healthy"
    })
    return {"status": "healthy", "service": "subtraction-service"}

@app.get("/", response_model=SubtractionResult, tags=["operations"])
async def subtract_numbers(
    first_number: float = 0, 
    second_number: float = 0
) -> SubtractionResult:
    """
    Subtract second number from first number.
    
    - **first_number**: The number to subtract from (minuend)
    - **second_number**: The number to subtract (subtrahend)
    
    Returns the difference of the two numbers.
    """
    try:
        result = subtraction(first_number, second_number)
        return SubtractionResult(
            result=result,
            first_number=first_number,
            second_number=second_number
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
