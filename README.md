# lexiconBased_SA_NL
Kode untuk melakukan analisis sentimen berbasis leksikon pada kumpulan data Dutch

Folder ini berisi kode untuk melakukan analisis sentimen berbasis leksikon pada data Dutch.
Persyaratan:
* Instal CRF++ di virtual env . Anda
* Pastikan salinan lokal folder Lets Preprocess (https://github.ugent.be/lt3/lets) ke Pythonpath Anda
* Lihat pipfile

## General  info
* Batas kalimat dalam teks masukan harus ditunjukkan dengan token '[EOS]'.
* Negasi diperhitungkan (periksa kata-kata dalam daftar negasi di atas skrip)
* Label sentimen standar harus berkaitan dengan yang berikut: 'sangat_negatif', 'negatif', 'positif', 'sangat_positif', 'netral', 'objektif'
* Sistem mengeluarkan skor sentimen numerik per kalimat dan memetakannya ke pos/neg/neu untuk menghitung akurasi.
* Akurasi SA dicetak di terminal; jika Anda ingin menghitung ulang menggunakan outfile, Anda harus memetakan skor ke -1, 0.0 dan 1, seperti yang dilakukan oleh skrip.
* **!! Script memprediksi skor sentimen pada tingkat kalimat; Anda memutuskan bagaimana Anda menggabungkan prediksi pasca-level.**

Leksikon yang digunakan bersifat generik, sehingga kode dapat dijalankan pada beberapa jenis genre teks (media sosial, blog, teks surat kabar, resensi,...).
Ada empat leksika Dutch yang digunakan --> hanya entri dengan tag-PoS berikut yang dipertimbangkan: ADJ, WW, BW, N

Leksika dicari dalam urutan tertentu; yaitu jika kata yang diberikan tidak ditemukan dalam leksikon 1, maka akan dicari dalam leksikon 2, dll. Jika sebuah kata ditemukan dalam leksikon 1, maka pencarian lebih lanjut pada leksikon 2, 3 dan 4 tidak dilakukan. Urutan ini ditentukan secara eksperimental; tujuan percobaan ini adalah mencari tahu leksikon mana yang paling dapat diandalkan untuk analisis sentimen dalam urutan dari yang terbaik hingga yang terakhir.

## Script input
* Path to the input file; a tab-separated file wih a gold-standard label and the text to be analyzed (1 instance = 1 line; make sure to replace newlines within a post with '[EOS]' to indicate sentence boundaries!)
* Path to the output folder

## Script output
	* A tab-separated file with the gold label, the predicted label and the original text. Format: 1 sentence per line, instances are separated by empty lines.
	* A .txt file with all the sentiment words that were matched against the sentiment lexica (for qualitative analysis purposes).


### Lexicon references

@inproceedings{Desmedt2012,
    title = {''Vreselijk mooi!'' (terribly beautiful): A Subjectivity Lexicon for {D}utch Adjectives.},
    author = {De Smedt, Tom  and Daelemans, Walter},
    booktitle = {Proceedings of the Eighth International Conference on Language Resources and Evaluation ({LREC}'12)},
    month = may,
    year = {2012},
    address = {Istanbul, Turkey},
    publisher = {ELRA},
    url = {http://www.lrec-conf.org/proceedings/lrec2012/pdf/312_Paper.pdf},
    pages = {3568--3572}
}


@inproceedings{Jijkoun2009,
    author = {Jijkoun, Valentin and Hofmann, Katja},
    title = {Generating a Non-English Subjectivity Lexicon: Relations That Matter},
    year = {2009},
    publisher = {ACL},
    address = {USA},
    booktitle = {Proceedings of the 12th Conference of the European Chapter of the Association for Computational Linguistics},
    pages = {398–405},
    numpages = {8},
    location = {Athens, Greece},
    series = {EACL'09}
}

@article{Mohammad2013,
	author = {Mohammad, Saif M. and Turney, Peter D.},
	journal = {Computational Intelligence},
	number = {3},
	pages = {436--465},
	title = {Crowdsourcing a Word-Emotion Association Lexicon},
	volume = {29},
	year = {2013}
}
