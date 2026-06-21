import pytest
from cassis import Cas, TypeSystem
from src.crop_example.update_fs import update_fs, propagate_feature_values

@pytest.fixture
def typesystem():
    typesystem = TypeSystem()
    Annotation = typesystem.create_type(name='cassis.Annotation')
    typesystem.create_feature(domainType=Annotation, name='basic_feature', rangeType='uima.cas.String')
    
    Annotation_wDependencies = typesystem.create_type(name='UDependency')
    typesystem.create_feature(domainType=Annotation_wDependencies, name='Governor', rangeType='cassis.Annotation')
    typesystem.create_feature(domainType=Annotation_wDependencies, name='Dependent', rangeType='cassis.Annotation')
    
    return typesystem

@pytest.fixture
def cas(typesystem):
    return Cas(typesystem=typesystem)

def test_update_fs_success(cas, typesystem):
    Annotation = typesystem.get_type('cassis.Annotation')
    fs_target = Annotation(begin=0, end=5)
    fs_origin = Annotation(begin=10, end=15)
    fs_origin.basic_feature = "value1"
    
    update_fs(fs_target, 'basic_feature', fs_origin, 'basic_feature')
    
    assert fs_target.basic_feature == "value1"

def test_update_fs_target_feature_missing(cas, typesystem):
    Annotation = typesystem.get_type('cassis.Annotation')
    fs_target = Annotation(begin=0, end=5)
    fs_origin = Annotation(begin=10, end=15)
    fs_origin.basic_feature = "value1"
    
    with pytest.raises(AttributeError):
        update_fs(fs_target, 'non_existent', fs_origin, 'basic_feature')

def test_update_fs_origin_feature_missing(cas, typesystem):
    Annotation = typesystem.get_type('cassis.Annotation')
    fs_target = Annotation(begin=0, end=5)
    fs_origin = Annotation(begin=10, end=15)
    
    with pytest.raises(AttributeError):
        update_fs(fs_target, 'basic_feature', fs_origin, 'non_existent')

def test_update_from_dependent_fs_success(cas, typesystem):
    Annotation = typesystem.get_type('cassis.Annotation')
    Annotation_wDependencies = typesystem.get_type('UDependency')
    
    gov = Annotation(begin=0, end=10)
    dep = Annotation(begin=5, end=15)
    
    anno = Annotation_wDependencies(begin=0, end=0)
    anno.Governor = gov
    anno.Dependent = dep
    
    cas.add(gov)
    cas.add(dep)
    cas.add(anno)
    
    # Update end from Governor
    propagate_feature_values(cas, 'UDependency', 'end', 'Governor')
    assert anno.end == 10
    
    # Update begin from Dependent
    propagate_feature_values(cas, 'UDependency', 'begin', 'Dependent')
    assert anno.begin == 5

