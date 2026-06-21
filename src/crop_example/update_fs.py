"""
This module provides functions to update feature structures in a UIMA CAS.
It specifically helps in propagating feature values (like begin/end offsets) 
from one feature structure to another based on dependencies.
"""
from cassis import Cas, load_cas_from_xmi, load_typesystem
from cassis.typesystem import FeatureStructure

def update_fs(target_fs: FeatureStructure, target_feature: str, origin_fs: FeatureStructure, origin_feature: str):
    """
    Updates a feature in the target feature structure with a value from the origin feature structure.

    Args:
        target_fs: The feature structure to be updated.
        target_feature: The name of the feature to update in target_fs.
        origin_fs: The feature structure to get the value from.
        origin_feature: The name of the feature to get the value from in origin_fs.
    """
    if target_feature not in [f.name for f in target_fs.type.all_features]:
        raise AttributeError(f"Feature [{target_feature}] not available in target feature structure [{target_fs.type}]")
    if origin_feature not in [f.name for f in origin_fs.type.all_features]:
         raise AttributeError(f"Feature [{origin_feature}] not found in origin feature structure [{origin_fs.type}]")
    target_fs[target_feature] = origin_fs[origin_feature]


def propagate_feature_values(tmp_cas: Cas, target_type: str, target_feature: str, target_dependent: str, origin_feature:str = None):
    """
    Updates a feature of a target type based on a feature of a dependent feature structure.

    This function iterates over all feature structures of target_type in the CAS and 
    updates their target_feature using the value from origin_feature of the 
    feature structure linked via target_dependent.

    Args:
        tmp_cas: The CAS containing the feature structures.
        target_type: The type of the feature structures to update.
        target_feature: The name of the feature to update in the target feature structures.
        target_dependent: The name of the feature in the target that links to the origin feature structure.
        origin_feature: The name of the feature in the origin feature structure to copy from. 
                        If None, target_feature is used.
    """
    if not origin_feature:
        origin_feature = target_feature
    for target in tmp_cas.select(target_type):
        update_fs(target, target_feature, target.get(target_dependent), origin_feature)


if __name__ == "__main__":
    xmi = open("../data/cas_dakoda.xmi").read()
    xml = open("../data/typesystem_dakoda.xml").read()
    cas_org = load_cas_from_xmi(xmi, typesystem=load_typesystem(xml))
    cas_org = cas_org.get_view("ctok")
    propagate_feature_values(cas_org, "UDependency", "end", "Governor")
    propagate_feature_values(cas_org, "UDependency", "begin", "Dependent")
    results = cas_org.select("UDependency")
    print(results)

