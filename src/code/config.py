import os


class Config:
    SERVER_ADDRESS = "3.125.95.236:8188"  #os.getenv("MODEL_ID")
    WORKFLOW_CHARACTER = "src/character-design-workflow.json"#os.getenv("TABLE_NAME")
    WORKFLOW_OBSTACLE = "src/obstacle-design-workflow.json"#os.getenv("TABLE_NAME")
    WORKFLOW_BACKGROUND = "src/background-design-workflow.json"#os.getenv("TABLE_NAME")