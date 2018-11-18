from PIL import Image, ImageDraw, ImageFont
 
PATH = "/home/davi/Documentos/Mestrado/Projeto_IA_SD/"

for i in range(1000):
	img = Image.new('RGB', (300, 300), color = (0, 0, 0))
	 
	fnt = ImageFont.truetype(PATH + 'arial.ttf', 110)
	d = ImageDraw.Draw(img)
	d.text((100,90), str(i), font=fnt, fill=(255, 255, 0))
	 
	img.save(PATH + "examples/" + str(i) + '.png')	