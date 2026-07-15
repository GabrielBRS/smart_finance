from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

def normalize(people: list[Person]) -> None:
    for p in people:
        p.name = p.name.strip().title()   # muta o atributo do objeto
        p.age += 1                          # idem
    print(people)

people = [Person("  gabriel ", 30), Person("matheus", 28)]
normalize(people)
print(people)


def colecoesDados() -> str:
    palavra = "pessoa"
    tamanho = len(palavra) - 1

    print(palavra[0])
    print(tamanho)
    return palavra[tamanho]


print(colecoesDados())


