import unittest
from mock import Mock

class Test(unittest.TestCase):
    def setUp(self):
        self.dm = dm.DialogManager()
        self.dm.dbi = Mock()

    def test_off_topic(self):
        self.assertEqual({'off_topic':"What can I call you?"}, self.dm.off_topic({"off_topic":"Hi"}))
        
    def test_command(self):
        self.dm.command({"command":dm.CLEAR})
        self.assertEqual(self.dm.state.get_all(),{})
        
    def test_request_director(self):
        self.dm.dbi.mockAddReturnValues(query=['James Cameron'])
        result=self.dm.request({'request':'director','title':'Titanic'})
        self.dm.dbi.mockCheckCall(0, 'query','director',{'title':'Titanic'}, count=None)
        self.assertEqual({'print':'director','results':['James Cameron']},result)
        
    def test_request_movies(self):
        condition={'director':'James Cameron'}
        self.dm.dbi.mockAddReturnValues(query=30)
        result=self.dm.request({'request':'title','director':'James Cameron'})
        self.dm.dbi.mockCheckCall(0, 'query','title',condition, count=None)
        self.assertEqual({'question':dm.MORE_PREF}, result)
        self.assertEqual(dm.MORE_PREF, self.dm.pending_question)
        
    def test_request_opinion1(self):
        condition = {"genre":"action","keyword":["dream","love"]}
        self.dm.dbi.mockAddReturnValues(query=7)
        request=dict(condition.items()+[('request',dm.OPINION)])
        result=self.dm.request(request)
        self.dm.dbi.mockCheckCall(0, 'query', 'title',condition, count=True)
        self.assertEqual({"list":7,"question":dm.SEE_RESULT}, result)

    def test_request_opinion2(self):
        condition = {"person":"Batman"}
        self.dm.dbi.mockAddReturnValues(query=70)
        result=self.dm.request({'request':dm.OPINION, "person":"Batman"})
        self.dm.dbi.mockCheckCall(0, 'query', 'title',condition, count=True)
        self.assertEqual({"list":70,"question":dm.MORE_PREF}, result)
        
    def test_request_count(self):
        condition={"actor":"Kate Winslet"}
        self.dm.dbi.mockAddReturnValues(query=2)
        result=self.dm.request({'request':dm.COUNT,'of':'Academy Award',"actor":"Kate Winslet"})
        self.dm.dbi.mockCheckCall(0, 'query', 'Academy Award',condition, count=True)
        self.assertEqual({'list':2,'question':dm.SEE_RESULT},result)
        
    def test_response_yes(self):
        self.dm.state = Mock()
        self.dm.pending_question=dm.SEE_RESULT
        self.dm.dbi.mockAddReturnValues(query=["Titanic", "The Reader"])
        self.dm.state.mockAddReturnValues(get_all={'actor':'Kate Winslet'},last_request='title')
        result = self.dm.response({'response':'YES'})
        self.dm.dbi.mockCheckCall(0, 'query', 'title', {'actor':'Kate Winslet'}, count=None)
        self.dm.state.mockCheckCall(2, 'add_request',{'request':'title','actor':'Kate Winslet'})
        self.assertEqual({'print':'title','results':["Titanic", "The Reader"]},result)
        
    def test_response_2(self):
        self.dm.state = Mock()
        self.dm.dbi.mockAddReturnValues(query=["Pirates of the Caribbean", "Pride and Prejudice"])
        self.dm.state.mockAddReturnValues(get_all={'request':'title','actor':'Keira Knightley'},last_request='title')
        self.dm.pending_question='result_length'
        result = self.dm.response({'response':2})
        self.dm.dbi.mockCheckCall(0, 'query', 'title', {'actor':'Keira Knightley'}, count=[0,2])
        self.dm.state.mockCheckCall(2, 'add_request',{'request':'title','actor':'Keira Knightley'})
        self.assertEqual({'print':'title','results':["Pirates of the Caribbean", "Pride and Prejudice"]},result)

    def test_request_similar(self):
        self.dm.dbi.mockAddReturnValues(query=['Dummy'])
        result = self.dm.request({'request':'SIMILAR','title':'Pirates of the Caribbean'})
        self.dm.dbi.mockCheckCall(0, 'query','director',{'title':'Pirates of the Caribbean'},[0,1])
        self.dm.dbi.mockCheckCall(1, 'query','genre',{'title':'Pirates of the Caribbean'},[0,1])
        self.dm.dbi.mockCheckCall(2, 'query','title',{'director':'Dummy','genre':'Dummy'},[0,50])
        
        self.assertEqual({'print':'title','results':["Dummy"]},result)
        
    def test_get_last_request(self):
        self.dm.dbi.mockAddReturnValues(query=['Dummy'])
        self.dm.request({'request':'title','person':'Tom Hanks'})
        self.assertEqual('title',self.dm.state.last_request())

if __name__ == "__main__":
    import sys
    sys.path.append("../")
    import dm
    unittest.main()
