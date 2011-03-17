import logging
class State:
    def __init__(self):
        self.states = []

    def clear(self):
        self.states[:] = []

    def get_all(self):
        lists = self.states[:]
        all_states = {}
        for dict in lists:
            for key in dict:
                if key == 'request' or key == 'results' or key == 'list':
                    continue
                # elif: a key is in all_states already
                elif all_states.has_key(key):
                    # if: eliminate duplicated values
                    if type(all_states[key]).__name__ == 'list' and dict[key] in all_states[key]:
                        continue
                    # elif: the value of the key is not a list yet, make it to
                    #     a list then append old value and add new value
                    elif type(all_states[key]).__name__ != 'list':
                        temp = all_states[key]
                        if temp != dict[key]:
                            all_states[key] = []
                            all_states[key].append(temp)
                            all_states[key].append(dict[key])
                    # else: the value of the key is a list, append directly
                    else:
                        if dict[key] in all_states[key]:
                            continue
                        elif type(dict[key]).__name__ == 'list':
                            for list_elem in dict[key]:
                                if list_elem not in all_states[key]:
                                    all_states[key].append(list_elem)
                        else:
                            all_states[key].append(dict[key])
                # else: add the key:value pair directly into the all_states dict
                else:
                    all_states[key] = dict[key]
        # log to session.log
        logging.debug("list= "+str(lists))
        logging.debug("all_states= "+str(all_states))
        return all_states

    def add_request(self, dict):
        self.states.append(dict)

    def add_result(self, dict):
        self.states.append(dict)

    def last_request(self):
        lists = self.states[:]
        lists.reverse()
        for dict in lists:
            if dict.has_key('request'):
                if dict['request'] == 'OPINION' and dict.has_key('title'):
                    return dict['title']
                elif dict['request'] == 'COUNT' and dict.has_key('of'):
                    return dict['of']
                return dict['request']
            else:
                continue

    def resolve_pronoun(self, value):
        # Find the last PRE_HE/PRE_IT.
        lists = self.states[:]
        lists.reverse()
        logging.debug("resolve_pronoun:states= "+str( lists) )
        for dict in lists:
            if value == 'PREV_HE':
                # Assuming actor/director are the only people we care about!
                if dict.has_key('actor') and dict['actor'] != 'PREV_HE':
                    return dict['actor']
                elif dict.has_key('person') and dict['person'] != 'PREV_HE':
                    return dict['person']
                elif dict.has_key('director') and dict['director'] != 'PREV_HE':
                    return dict['director']
            elif value == 'PREV_IT':
                # Assuming title is the only attribute PRE_IT will refer!
                if dict.has_key('title') and dict['title'] != 'PREV_IT':
                    if type(dict['title']).__name__ == 'list':
                        temp = dict['title']
                        temp.reverse()
                        logging.debug("resolve_pronoun:pre_it.list= "+str(temp[0]))
                        return temp[0]
                    else:
                        logging.debug("resolve_pronoun:pre_it.str= "+str( temp[0]))
                        return dict['title']
                    return dict['title']
        # user entered it/he/she but state doesn't have their info.
        return 'error'

    def delete_state(self, num_of_steps):
        # not needed but it doesn't hurt to have it.
        while num_of_steps > 0:
            self.states.pop()
            num_of_steps -= 1

#################################### Tests ####################################
if __name__ == '__main__':
    def print_dict(dict):
        for key in dict:
            print dict[key]

    state = State()
    state.add_request({'request':'director', 'title':'Titanic'})
    print '1st add => get_all:::::::'
    print state.get_all()
    print '1st add => last_request::::'
    print state.last_request() + '\n'

    state.add_request({'request':'title', 'director':'James Cameron'})
    print '2nd add => get_all:::::::'
    print state.get_all()
    print '2nd add => last_request::::::'
    print state.last_request() + '\n'

    state.add_request({'request':'OPINION', 'genre':'action', 'keyword':'dream'})
    print '3nd add => get_all:::::::'
    print state.get_all()
    print '3nd add => last_request::::::'
    print state.last_request() + '\n'

    state.add_request({'request':'OPINION', 'character':'Batman'})
    print '4nd add => get_all:::::::'
    print state.get_all()
    print '4nd add => last_request::::::'
    print state.last_request() + '\n'

    state.add_request({'request':'COUNT', 'of':'Academy Award', 'actor':'Kate Winslet'})
    print '5rd add => get_all:::::::'
    print state.get_all()
    print '5rd add => last_request::::::'
    print state.last_request() + '\n'

    print 'resolve PRE_IT ::::::::::::::::::::::::::'
    print state.resolve_pronoun('PRE_IT')
    print 'resolve PRE_HE ::::::::::::::::::::::::::'
    print state.resolve_pronoun('PRE_HE') + '\n'

    print 'delete one step ::::::::::::'
    state.delete_state(1)
    print state.get_all()

    print 'delete three step ::::::::::::'
    state.delete_state(3)
    print state.get_all()

    print 'before clear:::::::::::::::::::::::'
    print 'len(states) = ', len(state.states)
    for dict1 in state.states:
        print_dict(dict1)
    print 'after clear::::::::::::::::::::::::'
    state.clear()
    print 'len(states) = ', len(state.states), '\n'
