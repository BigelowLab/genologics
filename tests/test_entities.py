from unittest import TestCase
from xml.etree import ElementTree
from sys import version_info
from io import BytesIO

if version_info.major == 2:
    from mock import patch, Mock
    import __builtin__ as builtins
else:
    from unittest.mock import patch, Mock
    import builtins


from genologics.entities import StringDescriptor, StringAttributeDescriptor, StringListDescriptor, \
    StringDictionaryDescriptor, IntegerDescriptor, BooleanDescriptor, UdfDictionary


class TestEntities(TestCase):

    def test_pass(self):
        pass


class TestDescriptor(TestCase):

    def _make_desc(self, klass, *args, **kwargs):
        return klass(*args, **kwargs)

    def _tostring(self, e):
        outfile = BytesIO()
        ElementTree.ElementTree(e).write(outfile, encoding='utf-8', xml_declaration=True)
        return outfile.getvalue()


class TestStringDescriptor(TestDescriptor):

    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry>
<name>test name</name>
</test-entry>
""")
        self.instance = Mock(root=self.et)

    def test__get__(self):
        sd = self._make_desc(StringDescriptor, 'name')
        assert sd.__get__(self.instance, None) == "test name"

    def test__set__(self):
        sd = self._make_desc(StringDescriptor, 'name')
        sd.__set__(self.instance, "new test name")
        assert self.et.find('name').text == "new test name"


class TestStringAttributeDescriptor(TestDescriptor):

    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry name="test name">
</test-entry>""")
        self.instance = Mock(root=self.et)

    def test__get__(self):
        sd = self._make_desc(StringAttributeDescriptor, 'name')
        assert sd.__get__(self.instance, None) == "test name"


class TestStringListDescriptor(TestDescriptor):

    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry>
<test-subentry>A01</test-subentry>
<test-subentry>B01</test-subentry>
</test-entry>""")
        self.instance = Mock(root=self.et)

    def test__get__(self):
        sd = self._make_desc(StringListDescriptor, 'test-subentry')
        assert sd.__get__(self.instance, None) == ['A01', 'B01']


class TestStringDictionaryDescriptor(TestDescriptor):

    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry>
<test-subentry>
<test-firstkey/>
<test-secondkey>second value</test-secondkey>
</test-subentry>
</test-entry>""")
        self.instance = Mock(root=self.et)

    def test__get__(self):
        sd = self._make_desc(StringDictionaryDescriptor, 'test-subentry')
        res = sd.__get__(self.instance, None)
        assert type(res) == dict
        self.assertIsNone(res['test-firstkey'])
        assert res['test-secondkey'] == 'second value'

class TestIntegerDescriptor(TestDescriptor):

    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry>
<count>32</count>
</test-entry>
""")
        self.instance = Mock(root=self.et)

    def test__get__(self):
        sd = self._make_desc(IntegerDescriptor, 'count')
        assert sd.__get__(self.instance, None) == 32

    def test__set__(self):
        sd = self._make_desc(IntegerDescriptor, 'count')
        sd.__set__(self.instance, 23)
        assert self.et.find('count').text == 23
        # FIXME: The BooleanDescriptor (and the IntegerDescriptor) uses the StringDescriptor
        # Using them with their expected type makes serialization crash

class TestBooleanDescriptor(TestDescriptor):

    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry>
<istest>true</istest>
</test-entry>
""")
        self.instance = Mock(root=self.et)

    def test__get__(self):
        sd = self._make_desc(BooleanDescriptor, 'istest')
        assert sd.__get__(self.instance, None) == True

    def test__set__(self):
        # FIXME: The BooleanDescriptor (and the IntegerDescriptor) uses the StringDescriptor
        # Using them with their expected type makes serialization crash
        sd = self._make_desc(BooleanDescriptor, 'istest')
        sd.__set__(self.instance, False)
        assert self.et.find('istest').text == False
        #sd.__set__(self.instance, True)
        #print(self._tostring(self.et))
        #sd.__get__(self.instance, None)


class TestUdfDictionary(TestCase):
    def setUp(self):
        self.et = ElementTree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<test-entry xmlns:udf="http://genologics.com/ri/userdefined">
<udf:field type="String" name="test">stuff</udf:field>
<udf:field type="Numeric" name="how much">42</udf:field>
</test-entry>""")
        self.instance = Mock(root=self.et)
        self.dict1 = UdfDictionary(self.instance)
        self.dict2 = UdfDictionary(self.instance, udt=True)

    def _get_udf_value(self, udf_dict, key):
        for e in udf_dict._elems:
            if e.attrib['name'] != key:
                continue
            else:
                return e.text

    def test_get_udt(self):
        pass

    def test_set_udt(self):
        pass

    def test__update_elems(self):
        pass

    def test__prepare_lookup(self):
        pass

    def test___contains__(self):
        pass

    def test___getitem__(self):
        pass

    def test___setitem__(self):
        assert self._get_udf_value(self.dict1, 'test') == 'stuff'
        self.dict1.__setitem__('test', 'other')
        assert self._get_udf_value(self.dict1, 'test') == 'other'

        assert self._get_udf_value(self.dict1, 'how much') == '42'
        self.dict1.__setitem__('how much', 21)
        assert self._get_udf_value(self.dict1, 'how much') == '21'

        self.assertRaises(TypeError, self.dict1.__setitem__, 'how much', '433')

        #I'm not sure if this is the expected behaviour
        self.dict1.__setitem__('how much', None)
        assert self._get_udf_value(self.dict1, 'how much') == b'None'

    def test___delitem__(self):
        pass

    def test_items(self):
        pass

    def test_clear(self):
        pass

    def test___iter__(self):
        pass

    def test___next__(self):
        pass

    def test_get(self):
        pass

