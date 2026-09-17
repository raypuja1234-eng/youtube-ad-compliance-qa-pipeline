#azure opentelemetry integration

import os
import logging 
from azure.monitor.opentelemetry import configure_azure_monitor

# create a dedicated logger
logger = logging.getLogger("brand-guardian-telemetry")

def setup_telemetry():
    '''
    initializes azure monitor opentelemetry
    tracks: HTTP requests, database queries, errors, performance metrics 
    sends this data to azure monitor 

    it auto captures every API request 
    no need to manually log each endpoint
    
    '''
    #retrieve connection string 
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning("No instrumentation key found . Telemetry is DISABLED.")
        return

    #Configure the azure monitor
    try:
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name = "brand-guardian-tracer"
        )
        logger.info("Azure monitoring tracking enabled and connected")
    except Exception as e:
        logger.error(f"Failed to initialize azure monitor: {e}")
    
'''
why do we use telemetry?

without :
API is slow -> no idea which part 
how many users today ? no visibility

with:
audit endpoint averages 4.5 s (Indexer takes 3.8 s)
error logs show : 12% of audits fail due to youtube download errors
metrics show : 450API calls today ,89% success rate.
'''