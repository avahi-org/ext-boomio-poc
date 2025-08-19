from string import Template

GUIDE_PROMPT = Template(
    """
    Based on the information provided in the pdf please create the following assests to design a simple 2D mobile game used as a marketing campaign, you have to create: 
    1. The gamefication strategy 
    2. A general description of the game (if it is similar to another game tell me which one) 
    3. Description of the characters involved 
    4. Description of the stages used 
    5. General rules of the game. 
    Generate the result as a valid string format.
    """
)

GEN_IMG_PROMPT = Template(
    """
    Based on the information provided,
    generate a prompt for image generating 2D main character inside the describe game background. 
    Character name inside ** **. 
    Plain text
    """
)
