from Part import Part
# to write corrected output to file
import xml.etree.cElementTree as ET
# to convert characters to ascii
import unicodedata

# to handle unicode characters that unicodedata doesn't catch
Replacement_Dict = {u'\u2014':'-'}

def replace_unicode(text):
	for k in Replacement_Dict:
		text = text.replace(k, Replacement_Dict[k])
	return text

# An object to interpret words in hocr files
class Word(Part):
	def __init__(self, tag, et_parent=None):
		super(self.__class__, self).__init__(tag)
		# set text and clean up by changing all text to ascii (assuming we are working in English for the moment)
		self.text = tag.get_text()
		self.text = replace_unicode(self.text)
		self.text = unicodedata.normalize('NFKD', self.text).encode('ascii','ignore')
		self.corrected_text = None
		# record the id from the hocr document and the ocr text
		# so that we can audit the resulting xml document for acuracy
		if et_parent is not None:
			self.et = ET.SubElement(et_parent, "word", bbox=str(self.bbox), id=self.id, ocr_text=self.text)
		else:
			self.et = ET.Element("word", bbox=str(self.bbox), id=self.id, ocr_text=self.text)
		self.et.text = self.text

	def __repr__(self):
		if self.corrected_text is not None:
			return self.corrected_text
		return ''.join(filter(lambda x:ord(x) < 128, self.text))

	# I am making a word specific implementation of this so we can have fuzzy
	# matching for substrings (it is more likely that an OCR word contains two words than partial words)
	# this is the same as the line version except the long string is now the OCR one and the short
	# string is the correct one
	def levenshteinDistance(self, s1, s2_edge_cost=.01, s2_mid_cost=1, s1_cost=1, sub_cost=1):
		s2 = str(self)
		if len(s2.strip()) == 0:
			return 1.0
		# if we are matching lines we are interested in sub-strings
		# but in the word case it costs us more to add letters to
		# s1 (this string) than s2 (the word)
		cost_of_skipping_edge_s2_letters = s2_edge_cost
		cost_of_skipping_mid_s2_letters = s2_mid_cost
		cost_of_skipping_s1_letters = s1_cost
		cost_of_substatuting_letters = sub_cost
		distances = [v*cost_of_skipping_edge_s2_letters for v in range(len(s2) + 1)]
		for i1, c1 in enumerate(s1):
			# cost of starting here and skipping the rest of s2
			distances_ = [distances[0] + cost_of_skipping_s1_letters]
			for i2, c2 in enumerate(s2):
				if c1 == c2:
					# indexes are off by one since we start with the null position so this is
					# actually the value diaganally upwards from the current position
					distances_.append(distances[i2])
				else:
					skip_this_letter_in_s1 = distances[i2] + cost_of_skipping_s1_letters
					skip_this_letter_in_s2 = distances_[-1] + cost_of_skipping_mid_s2_letters
					substatute_this_letter = distances[i2 + 1] + cost_of_substatuting_letters
					distances_.append(min((skip_this_letter_in_s2, skip_this_letter_in_s1, substatute_this_letter)))
			distances = distances_
		# we need a final row on the bottom like the one on the top to add the cost of edge skips at the end
		final_distances = [distances[i]+(len(distances)-i-1)*cost_of_skipping_edge_s2_letters for i in range(len(distances))]
		return float(min(final_distances))/len(s1)

	def assign_matching(self, text):
		self.corrected_text = text
		self.et.text = text

	def scale(self, right_shift, down_shift, multiple):
		self.bbox.scale(right_shift, down_shift, multiple)
		self.et.set('bbox', str(self.bbox))