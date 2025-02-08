from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]
    

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise
        # plecam din q0
        current_state = self.q0
        # pentru fiecare caracter din cuvant
        for chr in word:
            # trecem in starea urmatore pe caracterul curent
            if (current_state, chr) in self.d:
                current_state = self.d[(current_state, chr)]
            else:
                return False
        # daca starea in care am ajuns este finala, cuvantul este acceptat
        if current_state in self.F:
            return True
        return False

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        pass
    
    
    def minimize(self) -> 'DFA[STATE]':
        states = self.K.copy()
        finals = self.F.copy()
        # partitia curenta
        P = {frozenset(finals), frozenset(states - finals)}
        # partitiile care trebuie verificate
        W = {frozenset(finals), frozenset(states - finals)}
        while W:
            Q = W.pop()
            for chr in self.S:
                # delta^(-1)(Q, chr)
                X = {state for state in self.K if (state, chr) in self.d and self.d[(state, chr)] in Q}
                X = frozenset(X)
                P_rebuild = set()
                # pentru fiecare partitie din P
                for part in P:
                    R1 = part & X
                    R2 = part - X
                    # daca R1 si R2 sunt nevide si nu sunt egale cu X
                    # le adaugam in partitia intermediara
                    if R1 and R2:
                        P_rebuild.add(R1)
                        P_rebuild.add(R2)
                        # daca partitia curenta se gaseste in W
                        # inlocuin in W partitia curenta cu R1 si R2
                        if part in W:
                            W.remove(part)
                            W.add(R1)
                            W.add(R2)
                        # daca nu, adaugam in W partitia cea mai mica
                        else:
                            if len(R1) <= len(R2):
                                W.add(R1)
                            else:
                                W.add(R2)
                    # daca R1 si R2 sunt vide sau egale cu X
                    # adaugam partitia curenta in partitia intermediara
                    else:
                        P_rebuild.add(part)
                # actualizam P la noua partitie
                P = P_rebuild.copy()
        # pentru a se respecta tipul starii pentru DFA,
        # trebuie sa etichetam partitiile din P cu o singura stare
        # astfel, pentru fiecare partitie, alegem ca stare reprezentativa
        # prima stare din partitie
        # ca sa putem accesa starile din interiorul partitiei,
        # transformam partitia intr-o lista si fiecare submultime in lista

        # transformam partitia P in lista
        list_P = list(P)
        # mapam fiecare stare la o stare reprezentativa din partitia sa
        mapping = {}
        for i in range(len(list_P)):
            list_P[i] = list(list_P[i])
            for state in list_P[i]:
                mapping[state] = list_P[i][0]
        # noile stari ale DFA-ului
        new_states = set(mapping.values())
        # construirea tranzitiilor
        new_transitions = {}
        for state in new_states:
            for chr in self.S:
                new_transitions[(state, chr)] = mapping[self.d[(state, chr)]]
        # starea initiala
        new_start = mapping[self.q0]
        # starile finale
        new_finals = {mapping[state] for state in finals}
        return DFA(self.S, new_states, new_start, new_transitions, new_finals)
        
        
        
        
        
        