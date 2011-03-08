import sys
from os import path 
current_dir = path.dirname(__file__)
sys.path.append(path.join(current_dir, ".."))
from dbi import dbi
import chatbot
from state import State

# TODO skip state when not opinion
# TODO shouldn't concatenate request
class DialogManager:
    def __init__(self):
        self.pending_question = None
        self.state = State()
        self.dbi = dbi #TODO initialize dbi here

    def request(self, dict):
        # NLG does not need to be aware of below operations
        # to dict, make a copy of dict to hide the operations
        internal_dict = dict.copy()
        # Resolve pronouns
        for key in internal_dict:
            if internal_dict[key] in ["PRE_HE", "PRE_IT"]:
                internal_dict[key] = self.state.resolve_pronoun(internal_dict[key])
        if internal_dict.has_key("result_length"):
            state_dict=internal_dict.copy()
            state_dict.pop("result_length")
            self.state.add_request(state_dict)
        else:
            self.state.add_request(internal_dict)
        internal_dict = self.state.get_all()
        request_type = internal_dict.pop("request")
        if request_type == OPINION:
            if internal_dict.has_key('title'):
                # the user is saying something like "I like it"
                return {}
            else:
                self.pending_question = HOW_MANY
                count=self.dbi.query('title',internal_dict, count=True)
                if count>10:
                    self.pending_question = HOW_MANY
                else:
                    self.pending_question = SEE_RESULT
                return {"list":count, "question":self.pending_question}
        elif request_type == COUNT:
            of = internal_dict.pop("of")
            count=self.dbi.query(of, internal_dict, count=True)
            result={}
            if count>10:
                self.pending_question = "result_length"
                result={"list":count, "question":HOW_MANY}
            else:
                self.pending_question = SEE_RESULT
                result={"list":count, "question":self.pending_question}
            return result
        else:
            results=self.dbi.query(request_type, internal_dict)
            if isinstance(results, int):
                if len(internal_dict)<2:
                    self.pending_question=MORE_PREF
                    return {"question":MORE_PREF}
                else:
                    self.pending_question = "result_length"
                    return {'print':request_type,"list":results, "question":HOW_MANY}
            else:
                return {'print':request_type,'results':results}
            
    
    def command(self, dict):
        if dict["command"]==CLEAR:
            self.state.clear()
    
    def response(self, dict):
        internal_dict = dict.copy()
        response = internal_dict.pop("response")
        if response=="NO":
            # FIXME check any problem here 
            return {}
        elif response == "YES":
            if self.pending_question:
                internal_dict["request"]=self.state.last_request()
        elif self.pending_question:
            internal_dict[self.pending_question]=response
            internal_dict["request"]=self.state.last_request()
        self.pending_question = None
        return self.request(internal_dict)
    
    def off_topic(self, dict):
        reply = chatbot.reply
        if reply is None:
            reply = chatbot.submit(dict['off_topic'])
        return {'off_topic':reply}
    
    def input(self, list):
        result_dict={}
        for dict in list:
            if dict.has_key("request"):
                result_dict.update(self.request(dict))
            elif dict.has_key("command"):
                self.command(dict)
            elif dict.has_key("response"):
                result_dict.update(self.response(dict))
            elif dict.has_key("off_topic"):
                result_dict=self.off_topic(dict)
        self.state.add_result(result_dict)
        return result_dict
        
# Define constants        
HOW_MANY = "HOW_MANY"
SEE_RESULT="SEE_RESULT?"
MORE_PREF="MORE_PREF"
EXIT="EXIT"
CLEAR="CLEAR"
COUNT="COUNT"
OPINION='OPINION'