import ocr_cleanup
# to write and read output
import csv
# to split by os seperator
import os
# to debug
import sys

def line_match_test(hocr_file, correct_filename):
	correct_bags = ocr_cleanup.get_correct_bags()
	doc = ocr_cleanup.Document(hocr_file, xml_dir='test-output')
	doc.assign_correct_bag(correct_filename, correct_bags[correct_filename])
	matched_lines, line_assignments, words_found = doc.get_line_matches(testing=True)
	for hocr_index, correct_index in enumerate(line_assignments):
		hocr_text = str(doc.lines[hocr_index])
		correct_text = -1 if correct_index == -1 else correct_bags[correct_filename][correct_index]
		wf = words_found.get(hocr_index, [])
		print hocr_text
		print '\t', correct_text
		print '\t', wf

def line_assignment_test(hocr_file, correct_filename):
	correct_bags = ocr_cleanup.get_correct_bags()
	doc = ocr_cleanup.Document(hocr_file, xml_dir='test-output')
	doc.assign_correct_bag(correct_filename, correct_bags[correct_filename])
	assignment = doc.assign_lines(testing=True)
	# check which lines are matched using the Levinstein Similarity
	# and which are matched on shared words
	matched_lines, line_assignments, words_found = doc.get_line_matches(testing=True)
	# save output to file
	stats_file = 'test-output' + os.sep + hocr_file.split(os.sep)[-1][:-len('.hocr')]+'.csv'
	with open(stats_file, 'w') as outfile:
		writer = csv.writer(outfile, delimiter=',', quotechar='"')
		writer.writerow(['Tesseract Line', 'Corrected Line', 'Matched Using Words'])
		for pair in assignment:
			matched_on_words = 1 if pair[1] is not None and correct_bags[correct_filename].index(pair[1]) in line_assignments else 0
			writer.writerow(list(pair) + [matched_on_words])

def line_similarity_test(hocr_file, correct_filename):
	correct_bags = ocr_cleanup.get_correct_bags()
	doc = ocr_cleanup.Document(hocr_file, xml_dir='test-output')
	stats_file = 'test-output' + os.sep + hocr_file.split(os.sep)[-1][:-len('.hocr')]+'_sim.csv'
	with open(stats_file, 'w') as outfile:
		writer = csv.writer(outfile, delimiter=',', quotechar='"')
		writer.writerow(['line'] + correct_bags[correct_filename])
		for l in doc.lines:
			row = [str(l)]
			for correct_string in correct_bags[correct_filename]:
				row.append(l.levenshteinDistance(correct_string))
			writer.writerow(row)

if __name__ == '__main__':
	line_assignment_test('test-data/sidebar-open.hocr', 'digital_reading_1.txt')