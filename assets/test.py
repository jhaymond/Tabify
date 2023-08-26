from Tabify.src.models.transcriber import Transcriber

t = Transcriber('test.musicxml')
tab = t.transcribe()
print(tab)
