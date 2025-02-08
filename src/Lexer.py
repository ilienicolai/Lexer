from .Regex import Regex, parse_regex
from .NFA import NFA
from .DFA import DFA
from .NFA import EPSILON
from functools import reduce

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # nfa final
        final_nfa : NFA = NFA(set(), set(), None, dict(), set())
        # stare initiala
        start_state = (-1, 'START', -1)
        # adaugam starea initiala
        final_nfa.K.add(start_state)
        # adaugam alfabetul
        final_nfa.q0 = start_state
        # adaugam tranzitiile
        final_nfa.d.update({(start_state, EPSILON): set()})
        # starile finale ale nfa-ului
        final_states1 = set()
        i = 0
        for token, regex in spec:
            # construim nfa-ul pentru fiecare regex
            nfa = parse_regex(regex).thompson()
            # remapam starile pentru a nu avea conflicte
            nfa = nfa.remap_states(lambda x: (x, i, token))
            # adaugam epsilon tranzitie de la starea initiala la starea initiala a nfa-ului
            final_nfa.d[(start_state, EPSILON)].add(nfa.q0)
            final_nfa.K.update(nfa.K)
            final_nfa.d.update(nfa.d)
            final_nfa.F.update(nfa.F)
            final_nfa.S.update(nfa.S)
            final_states1.add(nfa.F.pop())
            i += 1
        # nfa final
        self.nfa = final_nfa
        # starile finale
        self.final_states = final_states1
        # dfa-ul final
        self.dfa = final_nfa.subset_construction()

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        lexeme = []
        current_state = self.dfa.q0
        start_idx = 0
        # cat timp nu am terminat de parsat cuvantul
        while start_idx < len(word):
            # incepe de la starea initiala
            current_state = self.dfa.q0
            # ultima stare de acceptare
            last_accept_state = None
            # ultimul index de acceptare
            last_accept_idx = start_idx
            # verificare daca exista tranzitie
            trans_exists = True
            # de la indexul anterior pana la finalul cuvantului
            for idx in range(start_idx, len(word)):
                # daca exista tranzitie
                if (current_state, word[idx]) in self.dfa.d:
                    # trecem la urmatoarea stare
                    current_state = self.dfa.d[(current_state, word[idx])]
                    # retinem ultima stare de acceptare
                    if current_state in self.dfa.F:
                        last_accept_state = current_state
                        last_accept_idx = idx
                else:
                    trans_exists = False
                    break
            # daca am gasit o stare de acceptare
            if last_accept_state is not None:
                # frozenset cu ultima stare de acceptare
                fs = last_accept_state
                t_idx = 100000
                # set cu starile de acceptare
                notfs = set(fs)
                tk = ""
                # cautare token cu index cel mai mic
                # cautam in starile finale ale nfa-urilor
                for state in notfs:
                    # daca e stare finala in nfa
                    if state in self.final_states:
                        # daca indexul este mai mic
                        if state[1] < t_idx:
                            t_idx = state[1]
                            tk = state[2]
                # inserare token si lexem
                lexeme.append((tk, word[start_idx:last_accept_idx + 1]))
                # actualizare index de start
                start_idx = last_accept_idx + 1
            else:
                # eroare de parsare
                # extragere linie si caracter
                line_number = 0
                char_count = 0
                for i in range(0, start_idx + 1):
                    char_count += 1
                    if word[i] == "\n":
                        line_number += 1
                        char_count = 0
                # daca nu exista tranzitie
                if not trans_exists:
                    return [("", f"No viable alternative at character {char_count - 1}, line {line_number}")]
                # daca am ajuns la finalul cuvantului
                if start_idx >= len(word) - 1:
                    return [("", f"No viable alternative at character EOF, line {line_number}")]
                # daca nu am gasit stare de acceptare
                if last_accept_idx == start_idx:
                    return [("", f"No viable alternative at character {char_count}, line {line_number}")]
        return lexeme
        