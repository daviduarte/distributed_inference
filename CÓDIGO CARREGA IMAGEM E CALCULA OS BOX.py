		image = Image.open(PATH + "/imgs/2.png")
		print(image.getdata())
		(im_width, im_height) = image.size
		image = np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


		im = Image.open('imgs/2.png')
		im = im.resize((300, 300), Image.ANTIALIAS)
		draw = ImageDraw.Draw(im)


		#image = np.zeros((300,300,3))
		x = graph_global.get_tensor_by_name('prefix/image_tensor:0')
		y = graph_global.get_tensor_by_name('prefix/detection_boxes:0')

		with tf.Session(graph=graph_global) as sess:
			print("ok, criou a sessão")
			y_out = sess.run(y, feed_dict={
				x: np.expand_dims(image, 0)
			})


			for i in range(y_out.shape[1]):
				if all(np.array(y_out[0][i]) != np.array([0,0,0,0])):

					#print(x0)
					#print(x1)
					#print(y0)
					#rint(y1)

					x0 = y_out[0][i][0] * 300
					y0 = y_out[0][i][1] * 300
					x1 = y_out[0][i][2] * 300
					y1 = y_out[0][i][3] * 300

					#print(x0)
					#print(x1)
					#print(y0)
					#print(y1)
			
					draw.rectangle([y0, x0, y1, x1], outline="red")				

			del draw
			im.save("kkk.png", "PNG")

			#im = np.array(im, dtype=np.uint8)	