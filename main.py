'''
Main execution entry point for brand guardian AI.

This file is the "control centre" that starts and manages the entire 
compliance audit workflow . Think of it as the master switch that :
1. Sets up the audit request
2. runs the AI workflow
3. displays the final compliance report
'''

# Standard libary imports for basic Python functionality
import uuid        #generates unique IDs (like session tracking numbers)
import json        #handles JSON data formatting (converts Python dict to readable text)
import logging     # records what happens during execution(like a flight recorder)
from pprint import pprint    # Pretty-prints data structures (unused here, but available)


#Load environment variables from .env file
# This reads API Keys, database credentials , etc. without hardcoding them
from dotenv import load_dotenv
load_dotenv(override=True)  #override=True means .env values take priority over system variables

#import the main workflow graph (the brain of your compliance system)
from backend.src.graph.workflow import app

#configure logging - sets up the "flight recorder" for your application
logging.basicConfig(
    level = logging.INFO,    #INFO= show important events (DEBUG would show everything)
    format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #format : timestamp - loggername - severity - message
    # example : "2024-01-15 10:30:45 - brand-guardian - INFO - starting audit"
)
logger = logging.getLogger("brand-guardian-runner")   #creates a named logger for this module 

def run_cli_simulation():
    '''
    Simulates a video compliance audit request.

    this function orchestrates the entire audit process:
    - creates a unique session ID
    - prepares the video URL and metadata
    - runs it through the AI workflow 
    -displays the compliance results
    '''

    # =========STEP 1: Generate session ID ========== 
    session_id = str(uuid.uuid4())  #uuid4() generates random UUID 
    logger.info(f"Starting Audit session : {session_id}")   #Log to console/file


    # ====== STEP 2 : DEFINE INITIAL STATE =======
    #This dictionary contains all the input data for the workflow
    #Think of it as the "intake form" for the compliance audit
    initial_inputs = {
        # THE YOUTUBE video to audit
        "video_url" : "https://youtu.be/dT7S75eYhcQ",

        #Shortened video ID for easier tracking (first 8 chars of session ID)
        #Example : "vid_ce6c43bb"
        "video_id" : f"vid_{session_id[:8]}",

        # Empty list that will store compliance violation found
        #will be populated by the auditor node 
        "compliance_results" : [],

        #empty list for any errors during processing
        #example : ["Download failed", " Transcript unavailable"]
        "errors" : []
    }

    # ======= DISPLAY SECTION: INPUT SUMMARY =======
    print("n-----Initializing workflow......")
    # json.dumps() converts python dict to formatted JSON string
    # indent=2 makes it readable with 2-space indentation
    print(f"Input Payload : {json.dumps(initial_inputs,indent=2)}")

    # ===== STEP 3 : EXECUTE GRAPH ======
    # This is where the magic happens - runs the entire workflow
    try:
        # app.invoke() triggers the LangGraph workflow
        # It passes through : START -> INDEXER -> AUDITOR -> END
        # Returns the final state with all results
        final_state = app.invoke (initial_inputs)

        # ========= DISPLAY SECTION: EXECUTION COMPLETE =========
        print("\n-----Workflow execution complete-----")

        # ======= STEP 4 : OUTPUT RESULTS ========
        # Display a formatted compliance report

        print("\n Compliance Audit Report==")
        
        #.get() safely retrieves values (returns None if key doesn't exist)
        #Displays the video ID that was audited
        print(f"Video ID : {final_state.get('video_id')}")

        # Shows PASS or FAIL status
        print(f"Status : {final_state.get('final_status')}")

        # ======== VIOLATION SECTION =========
        print("\n [VIOLATIONS DETECTED]")

        # Extract the list of compliance violations 
        #Default to empty list if no results 
        results= final_state.get('compliance_results', [])
        if results:
            #Loop through each violation and display it
            for issue in results:
                # Each issue is a dict with : severity, category, descripion
                # example output: "-[CRITICAL] Misleading claims: absolute guarantee detected"
                print(f"- [{issue.get('severity')}] [{issue.get('category')}] [{issue.get('description')}]")
        else:
            # No violation found (clean video)
            print("No violations detected....")  

        # ======= SUMMMARY SECTION =======
        print("\n[FINAL SUMMARY]")
        #Display the AI-generated natural language summary 
        # example : " video contains 2 critical violation...."
        print(final_state.get('final_report'))

    except Exception as e:
        # ======= ERROR HANDLING =======
        # If anything breaks, log the error
        logger.error(f"Workflow Execution Failed : {str(e)}")

        # Re-raise the exception so we can see the full error trackback
        # This helps with debugging (shows exactly where/why it failed)
        raise e 


# ======== PROGRAM ENTRY POINT ==========
# This blocks only runs when you execute : python main.py
# It won't run when importing this file as a module in another file
if __name__ == "__main__":
    run_cli_simulation()   # Start the compliance audit simulation






