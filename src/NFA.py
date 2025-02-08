from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file
        reachables: set[STATE] = set() # set cu starile in care putem ajunge pe epsilon tranzitii
        reachables.add(state) # adaugam starea curenta
        state_que = [state] # coada cu starile care trebuie vizitate
        while state_que: # cat timp mai avem stari de vizitat
            current = state_que.pop()
            if (current, EPSILON) in self.d:
                for next_state in self.d[(current, EPSILON)]:
                    if next_state not in reachables:
                        # adaugam starea in care putem ajunge
                        reachables.add(next_state)
                        # adaugam starea in coada pentru a fi vizitata
                        state_que.append(next_state)
        return reachables

    def subset_construction(self) -> DFA[frozenset[STATE]]:  
        # convert this nfa to a dfa using the subset construction algorithm
        # determinam epsilon-closures pentru fiecare stare
        closures: dict[STATE, set[STATE]] = {state: self.epsilon_closure(state) for state in self.K}
        dfa_K = {frozenset(closures[self.q0])}
        dfa_d = {}
        dfa_F = set()
        # coada cu starile pe care trebuie sa le vizitam
        # incepem cu epsilon-closure pentru starea initiala
        state_que = [frozenset(closures[self.q0])]
        while state_que:
            current = state_que.pop()
            # verificam daca starea curenta este finala
            for state in current:
                if state in self.F:
                    dfa_F.add(current)
                    break
            # pentru fiecare simbol din alfabet si pentru fiecare stare din current
            for chr in self.S:
                if chr == EPSILON:
                    continue
                next_state = set()
                # calculam epsilon-closure pentru starile in care putem ajunge
                for state in current:
                    if (state, chr) in self.d:
                        for next_st in self.d[(state, chr)]:
                            # construim starea urmatoare
                            next_state |= closures[next_st]
                next_state = frozenset(next_state)
                # daca starea nu a fost vizitata o adaugam in coada
                # si in multimea starilor dfa-ului
                if next_state not in dfa_K:
                    dfa_K.add(next_state)
                    state_que.append(next_state)
                current_froze = frozenset(current)
                # adaugam tranzitia din current in next_state pe caracterul character
                dfa_d[(current_froze, chr)] = next_state
        return DFA(self.S, dfa_K, frozenset(closures[self.q0]), dfa_d, dfa_F)
        
        

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        rename_K = {f(state) for state in self.K}
        rename_d = {(f(state), char): {f(next_state) for next_state in next_states} for (state, char), next_states in self.d.items()}
        rename_F = {f(state) for state in self.F}
        return NFA(self.S, rename_K, f(self.q0), rename_d, rename_F)
    
    
