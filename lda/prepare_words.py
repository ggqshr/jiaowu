import sys
sys.path.append("..")
from prepare.config import db
from utils.clean_utils import filter_stop_words,SubFirstNameMatch
from pathlib import Path
from pickle import dump

cut_word_pos_col = db.get_collection("pos_words")

all_item = cut_word_pos_col.find({},{"all_words_filter":True},no_cursor_timeout=True)

obj = SubFirstNameMatch()

lda_data_path = Path("../data/lda")
lda_data_path.mkdir(exist_ok=True)
data_file = lda_data_path.joinpath("filter_words.pth")
all_data = []

for item in all_item:
    words = item.get("all_words_filter")
    words = [obj.sub_match(word) for word in words]
    words = list(filter(lambda x:not filter_stop_words(x),words))
    all_data.append(words)

with data_file.open(mode="wb") as f:
    dump(all_data,f)
