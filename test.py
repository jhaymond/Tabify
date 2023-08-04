from transcriber import Transcriber

t = Transcriber()
tab = t.transcribe('test.musicxml')
print(tab.fingerings)
