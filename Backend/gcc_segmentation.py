class GCCSegmentation:
    def __init__(self):
        """
        - This class is used for segmenting Khmer text based on the GCC (Khmer Character Cluster) rules.
        - It defines various sets of characters used in Khmer text, including consonants, vowels, independent vowels, diacritics, symbols, numbers, and lunar characters.
        - The `is_khmer_char` method checks if a character is a valid Khmer character.
        - The `is_start_of_kcc` method checks if a character is the start of a Khmer character cluster.
        - The `convert` method replaces characters in a text based on a predefined mapping.  
        - The `seg_gcc` method segments a sentence into Khmer character clusters based on the GCC rules.
        - The class uses Unicode character ranges and specific sets to identify Khmer characters and symbols.   
        """
        self.KHCONST = set(u'កខគឃងចឆជឈញដឋឌឍណតថទធនបផពភមយរលវឝឞសហឡអឣឤឥឦឧឨឩឪឫឬឭឮឯឰឱឲឳ')
        self.KHVOWEL = set(u'឴឵ាិីឹឺុូួើឿៀេែៃោៅ\u17c6\u17c7\u17c8')
        self.ENGCONST = set(u'abcdefghijklmnopqrstuvwxyz')
        self.KHSUB = set(u'្')
        self.KHDIAC = set(u"\u17c9\u17ca\u17cb\u17cc\u17cd\u17ce\u17cf\u17d0")
        self.KHSYM = set(u'៕។៛ៗ៚៙៘,.?')
        self.KHNUMBER = set(u'០១២៣៤៥៦៧៨៩')
        self.ENGNUMBER = set(u'0123456789')
        self.KHLUNAR = set(u'᧠᧡᧢᧣᧤᧥᧦᧧᧨᧩᧪᧫᧬᧭᧮᧯᧰᧱᧲᧳᧴᧵᧶᧷᧸᧹᧺᧻᧼᧽᧾᧿')
        self.KHSYMBOL = set(u')(][!@#$%^&*{}+-=_\u0027\u0022')
        # self.escapeCharacters = ['\n', '\r', '\t']

    def is_khmer_char(self, ch):
        if ('\u0041' <= ch <= '\u007A') or ('\u1780' <= ch <= '\u17FF'): return True
        if ch in self.KHSYM: return True
        if ch in self.KHLUNAR: return True
        if ch in self.KHSYMBOL: return True 
        if ch in self.ENGNUMBER: return True
        return False

    def is_start_of_kcc(self, ch):
        if self.is_khmer_char(ch):
            if ch in self.KHCONST: return True
            if ch in self.KHSYM: return True
            # if ch in self.KHNUMBER: return True
            if ch in self.KHLUNAR: return True
            # if ch in self.ENGCONST: return True
            if ch in self.KHSYMBOL: return True
            if ch in self.KHDIAC: return True
            # if ch in self.ENGNUMBER: return True
            return False
        return True

    def convert(self, text):
        convertedText = ''
        for character in text:
            if character in self.escapeCharacters:
                convertedText += character
            else:
                convertedText += self.characterUnicodes.get(character, character)
        return convertedText

    def seg_gcc(self, sentence):
        if sentence is None:
            print("Input is None")
            return []
        segs = []
        cur = ""
        for word in sentence.split('\u200b'):
            for i,c in enumerate(word):
                cur += c
                nextchar = word[i+1] if (i+1 < len(word)) else ""

                # cluster non-khmer chars together
                if not self.is_khmer_char(c) and nextchar != " " and nextchar != "" and not self.is_khmer_char(nextchar):
                    continue
                # cluster number together
                if c in self.KHNUMBER and nextchar in self.KHNUMBER :
                    continue
                if not self.is_khmer_char(c) or nextchar==" " or nextchar=="":
                    segs.append(cur)
                    cur=""
                elif self.is_start_of_kcc(nextchar) and not (c in self.KHSUB):
                    segs.append(cur)
                    cur=""
        return segs 
