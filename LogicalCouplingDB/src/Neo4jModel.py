from neomodel import *

import util
from util import File


class Coupled(StructuredRel):
    files = ArrayProperty(JSONProperty(), required=True, unique_index=True)
    coupled = BooleanProperty(default=False)
    magnitude = IntegerProperty(required=True)


class Component(StructuredNode):
    name = StringProperty(unique_index=True)
    coupled = RelationshipTo('Component', 'COUPLED', model=Coupled)


def addCouples(component1: util.Component, component2: util.Component, files_coupled: list[File]) -> list:
    inferred_comp_1 = Component(name=component1.name)
    inferred_comp_2 = Component(name=component2.name)

    comp_1 = inferred_comp_1.nodes.get_or_none(name=component1.name)
    comp_2 = inferred_comp_2.nodes.get_or_none(name=component2.name)

    if comp_1 is None:
        comp_1 = inferred_comp_1.save()
    if comp_2 is None:
        comp_2 = inferred_comp_2.save()

    rel = comp_1.coupled.relationship(comp_2)

    if rel is None:
        rel = comp_1.coupled.connect(comp_2, {'files': files_coupled, 'magnitude': 1})
    else:
        rel.files += files_coupled
        rel.magnitude += 1

    if rel.magnitude >= 5:
        rel.coupled = True

    rel.save()


def getComponentsCoupled() -> list[tuple[util.Component, util.Component]]:
    components = Component.nodes.all()
    coupled = []
    for component in components:
        rels = component.coupled.all()
        for rel in rels:
            if rel.coupled:
                coupled.append((component.name, rel.end_node.name))
    return coupled
