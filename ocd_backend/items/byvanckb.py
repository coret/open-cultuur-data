from datetime import datetime

from ocd_backend.items import BaseItem

class ByvanckBItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcx': 'http://krait.kb.nl/coop/tel/handbook/telterms.html',
        'dcterms': 'http://purl.org/dc/terms/',
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'xml': 'http://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=dcx' % original_id
        }

    def get_collection(self):
        return u'Koninklijke Bibliotheek - ByvanckB'

    def get_rights(self):
        return u'Public Domain Mark'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//dc:title')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//dc:description')
        if description:
            combined_index_data['description'] = description

        date = self._get_text_or_none('.//dc:date')
        if date:
            try:
                combined_index_data['date'] = datetime.strptime(date.replace(' (c.)', '').strip(), '%Y')
                combined_index_data['date_granularity'] = 4
            except ValueError:
                pass

        authors = self._get_text_or_none('.//dc:creator')
        if authors:
            combined_index_data['authors'] = [authors]

        mediums = self.original_item.xpath('.//dcx:illustration',
                                           namespaces=self.namespaces)
        if mediums:
            combined_index_data['media_urls'] = []

            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': medium.text,
                    'content_type': 'image/jpeg'
                })

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//dc:title'))

        # Creator
        text_items.append(self._get_text_or_none('.//dc:creator'))

        # Subject
        subjects = self.original_item.findall('.//dc:subject',
                                              namespaces=self.namespaces)
        for subject in subjects:
            text_items.append(unicode(subject.text))

        # Description
        text_items.append(self._get_text_or_none('.//dc:description'))

        # Publisher
        text_items.append(self._get_text_or_none('.//dc:source'))

        # Identifier
        text_items.append(self._get_text_or_none('.//dc:identifier'))

        # Type
        text_items.append(self._get_text_or_none('.//dc:type'))

        # Spatial
        text_items.append(self._get_text_or_none('.//dcterms:spatial'))

        return u' '.join([ti for ti in text_items if ti is not None])
