import os


class Config:
    SERVER_ADDRESS = "3.125.95.236:8188"  #os.getenv("MODEL_ID")
    WORKFLOW_CHARACTER = "scr/character-design-workflow.json"#os.getenv("TABLE_NAME")
    WORKFLOW_OBSTACLE = "scr/obstacle-design-workflow.json"#os.getenv("TABLE_NAME")
    WORKFLOW_BACKGROUND = "scr/background-design-workflow.json"#os.getenv("TABLE_NAME")