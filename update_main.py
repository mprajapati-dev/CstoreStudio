import re
import sys

with open("services/ai-agent/main.py", "r") as f:
    content = f.read()

# I will replace the LangGraph functions
new_nodes = """
from pydantic_ai import Agent
from pydantic import Field

class AIDiagnosis(BaseModel):
    identified_problem: str = Field(description="The identified issue from the image.")
    estimated_hours: float = Field(description="Estimated hours to fix the problem.")
    is_diy: bool = Field(description="Is this fixable by the store clerk?")

triage_agent = Agent('gemini-1.5-pro', result_type=AIDiagnosis)

@triage_latency.time()
def triage_and_estimate(state: JobState):
    print("STARTING triage_and_estimate")
    clerk_note = state.get('clerk_note', '')
    category = state.get('category', 'General')
    media_url = state.get('media_url', '')
    
    # 1. Pydantic-AI run (we stub the image binary for the demo to save memory, or pass URL directly if supported)
    # Using litellm/gemini proxy in Pydantic AI is possible, we just run import re
import sys

with oproimport sic
with opet r    content = f.read()

# I will replace the Lan r
# I will replace therunnew_nodes = """
from pydantic_ai importerfrom pydantic_e from pydantic import Field

ia
class AIDiagnosis(BaseMoexc    identified_problem: str pr    estimated_hours: float = Field(description="Estimated hours to fix the problem.")
ut    is_diy: bool = Field(description="Is this fixable by the store clerk?")

triage__n
triage_agent = Agent('gemini-1.5-pro', result_type=AIDiagnosis)

@triage_t"]
@triage_latency.time()
def triage_and_estimate(state: JobStats.idef triage_and_estimate    print("STARTING triage_and_estimate"
     clerk_note = state.get('clerk_note',      category = state.get('category', 'Generam    media_url = state.get('media_url', '')
   t     
    # 1. Pydantic-AI run (we stub tham   {'    # Using litellm/gemini proxy in Pydantic AI is possible, we just run import re
import sys

with oproimport siesimport sys

with oproimport sic
with opet r    content = f.read()

# I will repla  
with opr dywith opet r    conam
# I will replace the Lan r
# I  = # I will replace therunne
 from pydantic_ai importerfrom pydantint
ia
class AIDiagnosis(BaseMoexc    identified_problem: str pr    eEstcmaut    is_diy: bool = Field(description="Is this fixable by the store clerk?")

triage__n
triage_agent = Agent('gemini-1.5-pro', result_type=A)

triage__n
triage_agent = Agent('gemini-1.5-pro', result_type=AIDiagnosis)

gettriage_aeR
@triage_t"]
@triage_latency.time()
def triage_and_estimate(st_ho@triage_la  def triage_and_estima       clerk_note = state.get('clerk_note',      category = state.get('category', 'Generam    media_url =:    t     
    # 1. Pydantic-AI run (we stub tham   {'    # Using litellm/gemini proxy in Pydantic AI is possible, we just run implo    # 1.t)import sys

with oproimport siesimport sys

with oproimport sic
with opet r    content = f.read()

# I will repla  
with opr] 
with oprmps
with oproimport sic
with opetatwith opet r    con] 
# I will repla  
with opr dywit   with opr dywithat# I will replace the Lan r
# Id_# I  = # I will replace tte from pydantic_ai importerfrostatia
class AIDiagnosis(BaseMoexc    identtucn 
triage__n
triage_agent = Agent('gemini-1.5-pro', result_type=A)

triage__n
triage_agent = Agent('gemini-1.5-pro', result_type=AIDiagnosis)

getpastriage_a# 
triage__n
triage_agent = Agent('gemini-1.5-pro', rearttriage_aen
gettriage_aeR
@triage_t"]
@triage_latency.time()
def triage_aste@triage_t"]
sp@triage_laerdef triage_and_estimaat    # 1. Pydantic-AI run (we stub tham   {'    # Using litellm/gemini proxy in Pydantic AI is possible, we just run implo    # 1.t)import sys

with oproimport siesimport sys

wi_c
with oproimport siesimport sys

wi cat services/ai-agent/main_new.py | head -n 40
 '
