import glfw
import moderngl
import numpy as np
from PIL import Image

# Funzione per caricare texture da file
def load_texture(ctx, path):
	img = Image.open(path).convert('RGBA')  # Carichiamo la texture con alpha
	texture = ctx.texture(img.size, 4, img.tobytes())  # Creiamo la texture
	texture.build_mipmaps()
	texture.use()  # Usiamo la texture
	return texture

def main():
	# Inizializzazione GLFW
	if not glfw.init():
		return

	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
	glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

	window = glfw.create_window(800, 600, "Particle System", None, None)
	glfw.make_context_current(window)

	ctx = moderngl.create_context()

	# Vertex shader e Fragment shader
	prog = ctx.program(
		vertex_shader='''
		#version 330
		in vec3 in_pos;
		uniform mat4 projection;
		uniform mat4 model_view;
		void main() {
			gl_Position = projection * model_view * vec4(in_pos, 1.0);
			gl_PointSize = 32.0; // Dimensione del punto
		}
		''',
		fragment_shader='''
		#version 330
		uniform sampler2D particle_texture;
		out vec4 frag_color;
		void main() {
			vec4 tex_color = texture(particle_texture, gl_PointCoord);
			if (tex_color.a < 0.1)
				discard;
			frag_color = tex_color;
		}
		'''
	)

	# Posizioni delle particelle
	particle_positions = np.array([
		[-0.5,  0.5, 0.0],
		[ 0.5,  0.5, 0.0],
		[-0.5, -0.5, 0.0],
		[ 0.5, -0.5, 0.0],
	], dtype='f4')

	# Buffer delle particelle
	vbo = ctx.buffer(particle_positions)
	vao = ctx.simple_vertex_array(prog, vbo, 'in_pos')

	# Carichiamo la texture della particella
	texture = load_texture(ctx, './particle.png')

	# Matrice di proiezione e vista
	projection = np.eye(4, dtype='f4')  # Usa una matrice di proiezione fittizia
	model_view = np.eye(4, dtype='f4')  # Usa una matrice vista fittizia
	prog['projection'].write(projection)
	prog['model_view'].write(model_view)

	while not glfw.window_should_close(window):
		ctx.clear(0.1, 0.1, 0.1)

		texture.use()  # Usiamo la texture
		vao.render(moderngl.POINTS)  # Renderizza le particelle

		glfw.swap_buffers(window)
		glfw.poll_events()

	glfw.terminate()

if __name__ == "__main__":
	main()