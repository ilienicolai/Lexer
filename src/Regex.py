from typing import Any, List
from dataclasses import dataclass
from .NFA import NFA

EPSILON = ''

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex
    
def extract_tokens(reg: str) -> list[str]:
    regex_chars = []
    i = 0
    while i < len(reg):
        # adaugare operatori
        if reg[i] in ['*', '|', '+', '?', '(', ')']:
            regex_chars.append(reg[i])
        # adaugare interval de caractere
        elif reg[i] == '[':
            j = i
            while reg[j] != ']' and j < len(reg):
                j += 1
            regex_chars.append(reg[i:j+1])
            i = j
        # adaugare caractere escapate
        elif reg[i] == '\\' and i + 1 < len(reg):
            if reg[i + 1] in ['*', '|', '+', '[', ']', '/', '(', ')', '?', '\\']:
                regex_chars.append(reg[i:i+2])
            else:
                regex_chars.append(reg[i + 1])
        # salt peste spatiu
        elif reg[i] == ' ':
            i += 1
            continue
        # adaugare caracter din alfabet
        else:
            regex_chars.append(reg[i])
        i += 1
    return regex_chars
# parsare operatie de reuniune
def parse_union(regex_chars: list[str]) -> Regex:
    # lista de regex-uri pe care vom face reuniune
    regexes = []
    while regex_chars:
        # apelam funactia de ordin urmator - concatenare
        regexes.append(parse_concatenation(regex_chars))
        if regex_chars and regex_chars[0] == '|':
            regex_chars.pop(0)
        else:
            break
    # daca avem un singur regex, il returnam
    if len(regexes) == 1:
        return regexes[0]
    # altfel, facem reuniunea regex-urilor
    return Union(regexes)
# parsare operatie de concatenare
def parse_concatenation(regex_chars: list[str]) -> Regex:
    # lista de regex-uri pe care vom face concatenare
    regexes = []
    # cat timp avem doar operatii de concatenare
    while regex_chars and regex_chars[0] not in ['|', ')']:
        # apelam functia de ordin urmator - repetitie
        regexes.append(parse_repetition(regex_chars))
    # daca avem un singur regex, il returnam
    if len(regexes) == 1:
        return regexes[0]
    # altfel, facem concatenarea regex-urilor
    return Concatenation(regexes)

# parsare operatie de repetitie
def parse_repetition(regex_chars: list[str]) -> Regex:
    # apelam functia de ordin urmator (caracter sau (regex))
    regex = parse_atom(regex_chars)
    if regex_chars and regex_chars[0] == '*':
        regex_chars.pop(0)
        return Star(regex)
    if regex_chars and regex_chars[0] == '+':
        regex_chars.pop(0)
        return Plus(regex)
    if regex_chars and regex_chars[0] == '?':
        regex_chars.pop(0)
        return Question(regex)
    return regex

# parsare caracter sau grup de paranteze
def parse_atom(regex_chars: list[str]) -> Regex:
    # extragem token-ul curent
    token = regex_chars.pop(0)
    # daca am gasit un grup de paranteze, apelam functia de reuniune
    # si reluam procesul pentru grupul de paranteze
    if token == '(':
        sub_regex = parse_union(regex_chars)
        if not regex_chars or regex_chars[0] != ')':
            raise ValueError('missing closing parenthesis')
        regex_chars.pop(0)
        return sub_regex
    # daca am gasit un interval de caractere, il desfacem
    elif token.startswith('[') and token.endswith(']'):
        start = token[1]
        end = token[-2]
        if start == end:
            sub_regex = Character(start)
        else:
            characters = [chr(i) for i in range(ord(start), ord(end) + 1)]
            return Union([Character(char) for char in characters])
    # daca am gasit un caracter vom returna un obiect de tip Character
    # inclusiv pentru caracterele escapate
    elif len(token) == 1 or (len(token) == 2 and token[0] == '\\'):
        return Character(token)
    else:
        raise ValueError('invalid character')
def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string

    # you can define additional classes and functions to help with the parsing process

    # the checker will call this function, then the thompson method of the generated object. the resulting NFA's
    # behaviour will be checked using your implementation form stage 1
    # extragere elemente regex si adaugare in lista
    
    regex_chars = extract_tokens(regex)
    return parse_union(regex_chars)


@dataclass
class Character(Regex):
    chr: str
    
    def thompson(self) -> NFA[int]:
        start_state = 0
        final_state = 1
        # extragere caracter escapat
        if self.chr[0] == '\\':
            self.chr = self.chr[1]
        transitions = {(start_state, self.chr): {final_state}}
        return NFA({self.chr}, {start_state, final_state}, start_state, transitions, {final_state})

@dataclass
class Star(Regex):
    regex: Regex
    
    def thompson(self) -> NFA[int]:
        # determinare NFA pentru regex-ul din interiorul repetitiei
        rec_nfa = self.regex.thompson()
        start_state = 0
        final_state = 1
        # redenumire stari
        rec_nfa = rec_nfa.remap_states(lambda x: x + 2)
        # adaugaere noua stare initiala si finala
        rec_nfa.K.add(start_state)
        rec_nfa.K.add(final_state)
        # adaugare tranzitii din starea initiala
        rec_nfa.d.update({(start_state, EPSILON): set()})
        # catre starea initiala a NFA-ului
        rec_nfa.d[(start_state, EPSILON)].add(rec_nfa.q0)
        # catre starea finala
        rec_nfa.d[(start_state, EPSILON)].add(final_state)
        # adaugare tranzitii din starea finala
        rec_final = rec_nfa.F.pop()
        rec_nfa.d.update({(rec_final, EPSILON): set()})
        # catre starea initiala a NFA-ului
        rec_nfa.d[(rec_final, EPSILON)].add(rec_nfa.q0)
        # catre starea finala
        rec_nfa.d[(rec_final, EPSILON)].add(final_state)
        # setare noua stare initiala si finala
        rec_nfa.q0 = start_state
        rec_nfa.F = {final_state}
        return rec_nfa 

@dataclass
class Union(Regex):
    regexes: list[Regex]
    
    def thompson(self) -> NFA[int]:
        start_state = 0
        final_state = 1
        states = {start_state, final_state}
        transitions = {}
        alphabet = set()
        
        offset = 2
        transitions.update({(start_state, EPSILON): set()})
        for regex in self.regexes:
            # determinare NFA pentru fiecare regex
            rec_nfa = regex.thompson()
            # redenumire stari
            rec_nfa = rec_nfa.remap_states(lambda x: x + offset)
            # adaugare stari si tranzitii (update)
            states.update(rec_nfa.K)
            alphabet.update(rec_nfa.S)
            transitions.update(rec_nfa.d)
            # adaugare tranzitie din starea initiala catre starea initiala a NFA-ului
            transitions[(start_state, EPSILON)].add(rec_nfa.q0)
            # adaugare tranzitie din starea finala a NFA-ului catre starea finala
            transitions[(rec_nfa.F.pop(), EPSILON)] = {final_state}
            # incrementare offset cu numarul de stari ale NFA-ului
            offset += len(rec_nfa.K)
        return NFA(alphabet, states, start_state, transitions, {final_state})

@dataclass
class Concatenation(Regex):
    regexes: list[Regex]
    
    def thompson(self) -> NFA[int]:
        offset = 0
        states = set()
        alphabet = set()
        transitions = {}
        first_nfa = True
        prev_final_state = None
        for regex in self.regexes:
            # determinare NFA pentru fiecare regex interior concatenarii
            rec_nfa = regex.thompson()
            # redenumire stari
            rec_nfa = rec_nfa.remap_states(lambda x: x + offset)
            # adaugare stari si tranzitii (update)
            states.update(rec_nfa.K)
            alphabet.update(rec_nfa.S)
            transitions.update(rec_nfa.d)
            # daca nu este primul NFA, adaugam tranzitie de la starea finala a NFA-ului anterior
            # la starea initiala a NFA-ului curent
            if not first_nfa:
                transitions.update({(prev_final_state, EPSILON): set()})
                transitions[(prev_final_state, EPSILON)].add(rec_nfa.q0)
            # retinem starea finala a NFA-ului curent
            prev_final_state = rec_nfa.F.pop()
            # incrementare offset cu numarul de stari ale NFA-ului
            offset += len(rec_nfa.K)
            first_nfa = False
        return NFA(alphabet, states, 0, transitions, {prev_final_state})

@dataclass
class Plus(Regex):
    regex: Regex
    
    def thompson(self) -> NFA[int]:
        # determinare NFA pentru regex-ul din interiorul repetitiei
        rec_nfa = self.regex.thompson()
        start_state = 0
        final_state = 1
        # redenumire stari
        rec_nfa = rec_nfa.remap_states(lambda x: x + 2)
        # adaugare noua stare initiala si finala
        rec_nfa.K.add(start_state)
        rec_nfa.K.add(final_state)
        # adaugare tranzitii din starea initiala catre starea initiala a NFA-ului
        rec_nfa.d.update({(start_state, EPSILON): set()})
        rec_nfa.d[(start_state, EPSILON)].add(rec_nfa.q0)
        # adaugare tranzitii din starea finala
        rec_final = rec_nfa.F.pop()
        rec_nfa.d.update({(rec_final, EPSILON): set()})
        # catre starea finala a NFA-ului final
        rec_nfa.d[(rec_final, EPSILON)].add(final_state)
        # catre starea initiala a NFA-ului
        rec_nfa.d[(rec_final, EPSILON)].add(rec_nfa.q0)
        # setare noua stare initiala si finala
        rec_nfa.q0 = start_state
        rec_nfa.F = {final_state}
        return rec_nfa
    
@dataclass
class Question(Regex):
    regex: Regex
    def thompson(self) -> NFA[int]:
        # determinare NFA pentru regex-ul din interiorul repetitiei
        rec_nfa = self.regex.thompson()
        start_state = 0
        final_state = 1
        # redenumire stari
        rec_nfa = rec_nfa.remap_states(lambda x: x + 2)
        # adaugare noua stare initiala si finala
        rec_nfa.K.add(start_state)
        rec_nfa.K.add(final_state)
        # adaugare tranzitii din starea initiala
        rec_nfa.d.update({(start_state, EPSILON): set()})
        # catre starea initiala a NFA-ului
        rec_nfa.d[(start_state, EPSILON)].add(rec_nfa.q0)
        # catre starea finala
        rec_nfa.d[(start_state, EPSILON)].add(final_state)
        # adaugare tranzitii din starea finala a NFA-ului
        rec_final = rec_nfa.F.pop()
        rec_nfa.d.update({(rec_final, EPSILON): set()})
        # catre starea finala a NFA-ului final
        rec_nfa.d[(rec_final, EPSILON)].add(final_state)
        # setare noua stare initiala si finala
        rec_nfa.q0 = start_state
        rec_nfa.F = {final_state}
        return rec_nfa
