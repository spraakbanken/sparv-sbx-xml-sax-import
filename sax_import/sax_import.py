"""Efficient XML importer using SAX parsing."""

from sparv.api import AnnotationAllSourceFiles, Sourcem SourceFilename, SourceStructureParser

from xml.sax.handler import ContentHandler
from xml.sax import parse

def annotation_list_to_dict(annotation_list : list[AnnotationAllSourceFiles]) -> dict[str,AnnotationAllSourceFiles]:
    """Converts a list of AnnotationAllSourceFiles into a dictionary with the annotation/attribute name as key"""
    annotation_dict = {}
    for annotation in annotation_list:
        if annotation.attribute_name is not None:
            annotation_name = annotation.annotation_name + ":" + annotation.attribute_name
        else:
            annotation_name = annotation.annotation_name
        annotation_dict[annotation_name] = annotation
    return annotation_dict

class XMLStructure(SourceStructureParser):
    """Extracts the annotation structure from an XML file"""

    class XMLStructureHandler(ContentHandler):
        """Reads the xml structure from all XML files in the source directory"""
        annotations = []

        def startElement(self, name, attrs):
            """Callback for start tags"""
            if attrs:
                for a in attrs.getNames():
                    self.annotations.append(name + ":" + a)
            else:
                self.attributes.append(name)

    def get_annotations(self, corpus_config: dict) -> list[str]:
        """
        Return a list of annotations including attributes.

        Each value has the format 'annotation:attribute' or 'annotation'.
        Plain versions of each annotation ('annotation' without attribute) must be included as well.
        """
        xml_files = self.source_dir.glob("**/*.xml")
        annotations = []
        for file in xml_files:
            # The union of all attributes. Could make sense to have the intersection instead
            annotations += self.get_file_annotations(file)

    def get_file_annotations(self, file):
        """Parses the whole file using SAX parser and extracts all tags/elements as sparv annotations"""
        handler = XMLStructureHandler()
        parse(file, handler)
        return handler.annotations

class SAXParser(ContentHandler):
    """Parses an XML file into a sparv-ish structure using SAX parsing"""
    # The text content of the whole file
    text = []
    annotations = defaultdict(lambda:list())
    # keep track of the position of the start tag
    start_pos = {}
    text_len = 0
    open_tags = 0
    tag_count = 0
    blank_pattern = re.compile('^\\s+$')
    max_tags = 10 ** 7

    def startElement(self, name, attrs):
        """Callback for start tags"""
        self.open_tags += 1
        self.start_pos[name] = self.text_len
        for a in attrs.getNames():
            self.annotations[name + ":" + a].append(attrs.getValue(a))

    def endElement(self,name):
        """Callback for end tags"""
        self.annotations[name].append(((self.start_pos[name],self.open_tags),(self.text_len,self.open_tags)))
        self.open_tags -= 1

    def characters(self, content):
        """Callback for text content"""
        if not self.blank_pattern.match(content):
            self.text.append(content)
            self.text_len += len(content)

    def getText(self):
        return ''.join(self.text)

@importer("Test importer", file_extension = "xml",
          # Automatically extract the structure
          structure = XMLStructure)
def sax_import(source_file: SourceFilename = SourceFilename(),
          source_dir: Source = Source()
          ) -> None:
        parser = SAXParser()
        parse(source_dir.get_path(source_file,"xml"),parser)
        Text(source_file).write(parser.text)
        source_structure = list(parser.annotations.keys())
        SourceStructure(source_file).write(source_structure)
        for annotation_name in source_structure:
                Output(annotation_name, source_file=source_file).write(parser.annotations[annotation_name])
