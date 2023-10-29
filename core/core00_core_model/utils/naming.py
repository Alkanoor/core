

def classname_for(*class_dependencies):
    return ','.join(sorted(map(lambda x: x.__class__.__name__, class_dependencies)))

def tablename_for(*sqlalchemy_dependencies):
    return '|'.join(sorted(map(lambda x: x.__tablename__, sqlalchemy_dependencies)))

def limited_tablename_for(*sqlalchemy_dependencies, max_length=63):
    return '|'.join(sorted(map(lambda x: x.__tablename__, sqlalchemy_dependencies)))

def smart_tablename_for(*sqlalchemy_dependencies, max_length=63):
    return '|'.join(sorted(map(lambda x: x.__tablename__, sqlalchemy_dependencies)))