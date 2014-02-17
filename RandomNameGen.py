import random, sys

def main():
	with open('adjectives.txt') as f:
		adjectives = f.readlines()

	with open('animals.txt') as b:
		animals = b.readlines()

	if len(sys.argv) == 2:
		for i in xrange(int(sys.argv[1])):
			s1 = random.choice(adjectives).title()
			s2 = random.choice(animals)

			strpre = s1 + ' ' + s2 
			# strfinal = strpre.replace('\n', ' ')
			print strpre
	else:
		s1 = random.choice(adjectives).title()
		s2 = random.choice(animals)

		strpre = s1 + ' ' + s2 
		# strfinal = strpre.replace('\n', ' ')
		print strpre

if __name__ == '__main__':
	main()
