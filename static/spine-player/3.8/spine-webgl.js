var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var SceneRenderer = (function () {
			function SceneRenderer(canvas, camera) {
				this.canvas = canvas;
				this.camera = camera;
				this.batcher = new webgl.PolygonBatcher(context);
				this.shapes = new webgl.ShapeRenderer(context);
				this.skeletonDebugRenderer = new webgl.SkeletonDebugRenderer(context);
			}
			SceneRenderer.prototype.drawRegion = function (region, x, y, width, height, color, premultipliedAlpha) {
				if (color === void 0) { color = null; }
				if (premultipliedAlpha === void 0) { premultipliedAlpha = false; }
				this.enableRenderer(this.batcher);
				if (color === null)
					color = this.WHITE;
				var quad = this.QUAD;
				var i = 0;
				quad[i++] = x;
				quad[i++] = y;
				quad[i++] = color.r;
				quad[i++] = color.g;
				quad[i++] = color.b;
				quad[i++] = color.a;
				quad[i++] = region.u;
				quad[i++] = region.v2;
				if (this.twoColorTint) {
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
				}
				quad[i++] = x + width;
				quad[i++] = y;
				quad[i++] = color.r;
				quad[i++] = color.g;
				quad[i++] = color.b;
				quad[i++] = color.a;
				quad[i++] = region.u2;
				quad[i++] = region.v2;
				if (this.twoColorTint) {
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
				}
				quad[i++] = x + width;
				quad[i++] = y + height;
				quad[i++] = color.r;
				quad[i++] = color.g;
				quad[i++] = color.b;
				quad[i++] = color.a;
				quad[i++] = region.u2;
				quad[i++] = region.v;
				if (this.twoColorTint) {
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
				}
				quad[i++] = x;
				quad[i++] = y + height;
				quad[i++] = color.r;
				quad[i++] = color.g;
				quad[i++] = color.b;
				quad[i++] = color.a;
				quad[i++] = region.u;
				quad[i++] = region.v;
				if (this.twoColorTint) {
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
					quad[i++] = 0;
				}
				this.batcher.draw(region.texture, quad, this.QUAD_TRIANGLES);
			};
			SceneRenderer.prototype.line = function (x, y, x2, y2, color, color2) {
				if (color === void 0) { color = null; }
				if (color2 === void 0) { color2 = null; }
				this.enableRenderer(this.shapes);
				this.shapes.line(x, y, x2, y2, color);
			};
			SceneRenderer.prototype.triangle = function (filled, x, y, x2, y2, x3, y3, color, color2, color3) {
				if (color === void 0) { color = null; }
				if (color2 === void 0) { color2 = null; }
				if (color3 === void 0) { color3 = null; }
				this.enableRenderer(this.shapes);
				this.shapes.triangle(filled, x, y, x2, y2, x3, y3, color, color2, color3);
			};
			SceneRenderer.prototype.quad = function (filled, x, y, x2, y2, x3, y3, x4, y4, color, color2, color3, color4) {
				if (color === void 0) { color = null; }
				if (color2 === void 0) { color2 = null; }
				if (color3 === void 0) { color3 = null; }
				if (color4 === void 0) { color4 = null; }
				this.enableRenderer(this.shapes);
				this.shapes.quad(filled, x, y, x2, y2, x3, y3, x4, y4, color, color2, color3, color4);
			};
			SceneRenderer.prototype.rect = function (filled, x, y, width, height, color) {
				if (color === void 0) { color = null; }
				this.enableRenderer(this.shapes);
				this.shapes.rect(filled, x, y, width, height, color);
			};
			SceneRenderer.prototype.rectLine = function (filled, x1, y1, x2, y2, width, color) {
				if (color === void 0) { color = null; }
				this.enableRenderer(this.shapes);
				this.shapes.rectLine(filled, x1, y1, x2, y2, width, color);
			};
			SceneRenderer.prototype.polygon = function (polygonVertices, offset, count, color) {
				if (color === void 0) { color = null; }
				this.enableRenderer(this.shapes);
				this.shapes.polygon(polygonVertices, offset, count, color);
			};
			SceneRenderer.prototype.circle = function (filled, x, y, radius, color, segments) {
				if (color === void 0) { color = null; }
				if (segments === void 0) { segments = 0; }
				this.enableRenderer(this.shapes);
				this.shapes.circle(filled, x, y, radius, color, segments);
			};
			SceneRenderer.prototype.curve = function (x1, y1, cx1, cy1, cx2, cy2, x2, y2, segments, color) {
				if (color === void 0) { color = null; }
				this.enableRenderer(this.shapes);
				this.shapes.curve(x1, y1, cx1, cy1, cx2, cy2, x2, y2, segments, color);
			};
			SceneRenderer.prototype.end = function () {
				if (this.activeRenderer === this.batcher)
					this.batcher.end();
				else if (this.activeRenderer === this.shapes)
					this.shapes.end();
				this.activeRenderer = null;
			};
			SceneRenderer.prototype.resize = function (resizeMode) {
				var canvas = this.canvas;
				var w = canvas.clientWidth;
				var h = canvas.clientHeight;
				if (canvas.width != w || canvas.height != h) {
					canvas.width = w;
					canvas.height = h;
				}
				this.context.gl.viewport(0, 0, canvas.width, canvas.height);
				if (resizeMode === ResizeMode.Stretch) {
				}
				else if (resizeMode === ResizeMode.Expand) {
					this.camera.setViewport(w, h);
				}
				else if (resizeMode === ResizeMode.Fit) {
					var sourceWidth = canvas.width, sourceHeight = canvas.height;
					var targetWidth = this.camera.viewportWidth, targetHeight = this.camera.viewportHeight;
					var targetRatio = targetHeight / targetWidth;
					var sourceRatio = sourceHeight / sourceWidth;
					var scale = targetRatio < sourceRatio ? targetWidth / sourceWidth : targetHeight / sourceHeight;
					this.camera.viewportWidth = sourceWidth * scale;
					this.camera.viewportHeight = sourceHeight * scale;
				}
				this.camera.update();
			};
			SceneRenderer.prototype.enableRenderer = function (renderer) {
				if (this.activeRenderer === renderer)
					return;
				this.end();
				if (renderer instanceof webgl.PolygonBatcher) {
					this.batcherShader.bind();
					this.batcherShader.setUniform4x4f(webgl.Shader.MVP_MATRIX, this.camera.projectionView.values);
					this.batcherShader.setUniformi("u_texture", 0);
					this.batcher.begin(this.batcherShader);
					this.activeRenderer = this.batcher;
				}
				else if (renderer instanceof webgl.ShapeRenderer) {
					this.shapesShader.bind();
					this.shapesShader.setUniform4x4f(webgl.Shader.MVP_MATRIX, this.camera.projectionView.values);
					this.shapes.begin(this.shapesShader);
					this.activeRenderer = this.shapes;
				}
				else {
					this.activeRenderer = this.skeletonDebugRenderer;
				}
			};
			SceneRenderer.prototype.dispose = function () {
				this.batcher.dispose();
				this.batcherShader.dispose();
				this.shapes.dispose();
				this.shapesShader.dispose();
				this.skeletonDebugRenderer.dispose();
			};
			return SceneRenderer;
		}());
		webgl.SceneRenderer = SceneRenderer;
		var ResizeMode;
		(function (ResizeMode) {
			ResizeMode[ResizeMode["Stretch"] = 0] = "Stretch";
			ResizeMode[ResizeMode["Expand"] = 1] = "Expand";
			ResizeMode[ResizeMode["Fit"] = 2] = "Fit";
		})(ResizeMode = webgl.ResizeMode || (webgl.ResizeMode = {}));
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var Shader = (function () {
			function Shader(context, vertexShader, fragmentShader) {
				this.vertexShader = vertexShader;
				this.fragmentShader = fragmentShader;
				this.vs = null;
				this.fs = null;
				this.program = null;
				this.tmp2x2 = new Float32Array(2 * 2);
				this.tmp3x3 = new Float32Array(3 * 3);
				this.tmp4x4 = new Float32Array(4 * 4);
				this.vsSource = vertexShader;
				this.fsSource = fragmentShader;
				this.context = context instanceof webgl.ManagedWebGLRenderingContext ? context : new webgl.ManagedWebGLRenderingContext(context);
				this.context.addRestorable(this);
				this.compile();
			}
			Shader.prototype.getProgram = function () { return this.program; };
			Shader.prototype.getVertexShader = function () { return this.vertexShader; };
			Shader.prototype.getFragmentShader = function () { return this.fragmentShader; };
			Shader.prototype.getVertexShaderSource = function () { return this.vsSource; };
			Shader.prototype.getFragmentSource = function () { return this.fsSource; };
			Shader.prototype.compile = function () {
				var gl = this.context.gl;
				try {
					this.vs = this.compileShader(gl.VERTEX_SHADER, this.vertexShader);
					this.fs = this.compileShader(gl.FRAGMENT_SHADER, this.fragmentShader);
					this.program = this.compileProgram(this.vs, this.fs);
				}
				catch (e) {
					this.dispose();
					throw e;
				}
			};
			Shader.prototype.compileShader = function (type, source) {
				var gl = this.context.gl;
				var shader = gl.createShader(type);
				gl.shaderSource(shader, source);
				gl.compileShader(shader);
				if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
					var error = "Couldn't compile shader: " + gl.getShaderInfoLog(shader);
					gl.deleteShader(shader);
					if (!gl.isContextLost())
						throw new Error(error);
				}
				return shader;
			};
			Shader.prototype.compileProgram = function (vs, fs) {
				var gl = this.context.gl;
				var program = gl.createProgram();
				gl.attachShader(program, vs);
				gl.attachShader(program, fs);
				gl.linkProgram(program);
				if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
					var error = "Couldn't compile shader program: " + gl.getProgramInfoLog(program);
					gl.deleteProgram(program);
					if (!gl.isContextLost())
						throw new Error(error);
				}
				return program;
			};
			Shader.prototype.restore = function () {
				this.compile();
			};
			Shader.prototype.bind = function () {
				this.context.gl.useProgram(this.program);
			};
			Shader.prototype.unbind = function () {
				this.context.gl.useProgram(null);
			};
			Shader.prototype.setUniformi = function (uniform, value) {
				this.context.gl.uniform1i(this.getUniformLocation(uniform), value);
			};
			Shader.prototype.setUniformf = function (uniform, value) {
				this.context.gl.uniform1f(this.getUniformLocation(uniform), value);
			};
			Shader.prototype.setUniform2f = function (uniform, value, value2) {
				this.context.gl.uniform2f(this.getUniformLocation(uniform), value, value2);
			};
			Shader.prototype.setUniform3f = function (uniform, value, value2, value3) {
				this.context.gl.uniform3f(this.getUniformLocation(uniform), value, value2, value3);
			};
			Shader.prototype.setUniform4f = function (uniform, value, value2, value3, value4) {
				this.context.gl.uniform4f(this.getUniformLocation(uniform), value, value2, value3, value4);
			};
			Shader.prototype.setUniform2x2f = function (uniform, value) {
				var gl = this.context.gl;
				this.tmp2x2.set(value);
				gl.uniformMatrix2fv(this.getUniformLocation(uniform), false, this.tmp2x2);
			};
			Shader.prototype.setUniform3x3f = function (uniform, value) {
				var gl = this.context.gl;
				this.tmp3x3.set(value);
				gl.uniformMatrix3fv(this.getUniformLocation(uniform), false, this.tmp3x3);
			};
			Shader.prototype.setUniform4x4f = function (uniform, value) {
				var gl = this.context.gl;
				this.tmp4x4.set(value);
				gl.uniformMatrix4fv(this.getUniformLocation(uniform), false, this.tmp4x4);
			};
			Shader.prototype.getUniformLocation = function (uniform) {
				var gl = this.context.gl;
				var location = gl.getUniformLocation(this.program, uniform);
				if (!location && !gl.isContextLost())
					throw new Error("Couldn't find location for uniform " + uniform);
				return location;
			};
			Shader.prototype.getAttributeLocation = function (attribute) {
				var gl = this.context.gl;
				var location = gl.getAttribLocation(this.program, attribute);
				if (location == -1 && !gl.isContextLost())
					throw new Error("Couldn't find location for attribute " + attribute);
				return location;
			};
			Shader.prototype.dispose = function () {
				this.context.removeRestorable(this);
				var gl = this.context.gl;
				if (this.vs) {
					gl.deleteShader(this.vs);
					this.vs = null;
				}
				if (this.fs) {
					gl.deleteShader(this.fs);
					this.fs = null;
				}
				if (this.program) {
					gl.deleteProgram(this.program);
					this.program = null;
				}
			};
			Shader.newColoredTextured = function (context) {
				var vs = "\n\t\t\t\tattribute vec4 " + Shader.POSITION + ";\n\t\t\t\tattribute vec4 " + Shader.COLOR + ";\n\t\t\t\tattribute vec2 " + Shader.TEXCOORDS + ";\n\t\t\t\tuniform mat4 " + Shader.MVP_MATRIX + ";\n\t\t\t\tvarying vec4 v_color;\n\t\t\t\tvarying vec2 v_texCoords;\n\n\t\t\t\tvoid main () {\n\t\t\t\t\tv_color = " + Shader.COLOR + ";\n\t\t\t\t\tv_texCoords = " + Shader.TEXCOORDS + ";\n\t\t\t\t\tgl_Position = " + Shader.MVP_MATRIX + " * " + Shader.POSITION + ";\n\t\t\t\t}\n\t\t\t";
				var fs = "\n\t\t\t\t#ifdef GL_ES\n\t\t\t\t\t#define LOWP lowp\n\t\t\t\t\tprecision mediump float;\n\t\t\t\t#else\n\t\t\t\t\t#define LOWP\n\t\t\t\t#endif\n\t\t\t\tvarying LOWP vec4 v_color;\n\t\t\t\tvarying vec2 v_texCoords;\n\t\t\t\tuniform sampler2D u_texture;\n\n\t\t\t\tvoid main () {\n\t\t\t\t\tgl_FragColor = v_color * texture2D(u_texture, v_texCoords);\n\t\t\t\t}\n\t\t\t";
				return new Shader(context, vs, fs);
			};
			Shader.newTwoColoredTextured = function (context) {
				var vs = "\n\t\t\t\tattribute vec4 " + Shader.POSITION + ";\n\t\t\t\tattribute vec4 " + Shader.COLOR + ";\n\t\t\t\tattribute vec4 " + Shader.COLOR2 + ";\n\t\t\t\tattribute vec2 " + Shader.TEXCOORDS + ";\n\t\t\t\tuniform mat4 " + Shader.MVP_MATRIX + ";\n\t\t\t\tvarying vec4 v_light;\n\t\t\t\tvarying vec4 v_dark;\n\t\t\t\tvarying vec2 v_texCoords;\n\n\t\t\t\tvoid main () {\n\t\t\t\t\tv_light = " + Shader.COLOR + ";\n\t\t\t\t\tv_dark = " + Shader.COLOR2 + ";\n\t\t\t\t\tv_texCoords = " + Shader.TEXCOORDS + ";\n\t\t\t\t\tgl_Position = " + Shader.MVP_MATRIX + " * " + Shader.POSITION + ";\n\t\t\t\t}\n\t\t\t";
				var fs = "\n\t\t\t\t#ifdef GL_ES\n\t\t\t\t\t#define LOWP lowp\n\t\t\t\t\tprecision mediump float;\n\t\t\t\t#else\n\t\t\t\t\t#define LOWP\n\t\t\t\t#endif\n\t\t\t\tvarying LOWP vec4 v_light;\n\t\t\t\tvarying LOWP vec4 v_dark;\n\t\t\t\tvarying vec2 v_texCoords;\n\t\t\t\tuniform sampler2D u_texture;\n\n\t\t\t\tvoid main () {\n\t\t\t\t\tvec4 texColor = texture2D(u_texture, v_texCoords);\n\t\t\t\t\tgl_FragColor.a = texColor.a * v_light.a;\n\t\t\t\t\tgl_FragColor.rgb = ((texColor.a - 1.0) * v_dark.a + 1.0 - texColor.rgb) * v_dark.rgb + texColor.rgb * v_light.rgb;\n\t\t\t\t}\n\t\t\t";
				return new Shader(context, vs, fs);
			};
			Shader.newColored = function (context) {
				var vs = "\n\t\t\t\tattribute vec4 " + Shader.POSITION + ";\n\t\t\t\tattribute vec4 " + Shader.COLOR + ";\n\t\t\t\tuniform mat4 " + Shader.MVP_MATRIX + ";\n\t\t\t\tvarying vec4 v_color;\n\n\t\t\t\tvoid main () {\n\t\t\t\t\tv_color = " + Shader.COLOR + ";\n\t\t\t\t\tgl_Position = " + Shader.MVP_MATRIX + " * " + Shader.POSITION + ";\n\t\t\t\t}\n\t\t\t";
				var fs = "\n\t\t\t\t#ifdef GL_ES\n\t\t\t\t\t#define LOWP lowp\n\t\t\t\t\tprecision mediump float;\n\t\t\t\t#else\n\t\t\t\t\t#define LOWP\n\t\t\t\t#endif\n\t\t\t\tvarying LOWP vec4 v_color;\n\n\t\t\t\tvoid main () {\n\t\t\t\t\tgl_FragColor = v_color;\n\t\t\t\t}\n\t\t\t";
				return new Shader(context, vs, fs);
			};
			Shader.MVP_MATRIX = "u_projTrans";
			Shader.POSITION = "a_position";
			Shader.COLOR = "a_color";
			Shader.COLOR2 = "a_color2";
			Shader.TEXCOORDS = "a_texCoords";
			Shader.SAMPLER = "u_texture";
			return Shader;
		}());
		webgl.Shader = Shader;
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var ShapeRenderer = (function () {
			function ShapeRenderer(context, maxVertices) {
				if (maxVertices === void 0) { maxVertices = 10920; }
				this.isDrawing = false;
				this.shapeType = ShapeType.Filled;
				this.color = new spine.Color(1, 1, 1, 1);
				this.vertexIndex = 0;
				this.tmp = new spine.Vector2();
				if (maxVertices > 10920)
					throw new Error("Can't have more than 10920 triangles per batch: " + maxVertices);
				this.context = context instanceof webgl.ManagedWebGLRenderingContext ? context : new webgl.ManagedWebGLRenderingContext(context);
				this.mesh = new webgl.Mesh(context, [new webgl.Position2Attribute(), new webgl.ColorAttribute()], maxVertices, 0);
				this.srcBlend = this.context.gl.SRC_ALPHA;
				this.dstBlend = this.context.gl.ONE_MINUS_SRC_ALPHA;
			}
			ShapeRenderer.prototype.begin = function (shader) {
				if (this.isDrawing)
					throw new Error("ShapeRenderer.begin() has already been called");
				this.shader = shader;
				this.vertexIndex = 0;
				this.isDrawing = true;
				var gl = this.context.gl;
				gl.enable(gl.BLEND);
				gl.blendFunc(this.srcBlend, this.dstBlend);
			};
			ShapeRenderer.prototype.setBlendMode = function (srcBlend, dstBlend) {
				var gl = this.context.gl;
				this.srcBlend = srcBlend;
				this.dstBlend = dstBlend;
				if (this.isDrawing) {
					this.flush();
					gl.blendFunc(this.srcBlend, this.dstBlend);
				}
			};
			ShapeRenderer.prototype.setColor = function (color) {
				this.color.setFromColor(color);
			};
			ShapeRenderer.prototype.setColorWith = function (r, g, b, a) {
				this.color.set(r, g, b, a);
			};
			ShapeRenderer.prototype.point = function (x, y, color) {
				if (color === void 0) { color = null; }
				this.check(ShapeType.Point, 1);
				if (color === null)
					color = this.color;
				this.vertex(x, y, color);
			};
			ShapeRenderer.prototype.line = function (x, y, x2, y2, color) {
				if (color === void 0) { color = null; }
				this.check(ShapeType.Line, 2);
				var vertices = this.mesh.getVertices();
				var idx = this.vertexIndex;
				if (color === null)
					color = this.color;
				this.vertex(x, y, color);
				this.vertex(x2, y2, color);
			};
			ShapeRenderer.prototype.triangle = function (filled, x, y, x2, y2, x3, y3, color, color2, color3) {
				if (color === void 0) { color = null; }
				if (color2 === void 0) { color2 = null; }
				if (color3 === void 0) { color3 = null; }
				this.check(filled ? ShapeType.Filled : ShapeType.Line, 3);
				var vertices = this.mesh.getVertices();
				var idx = this.vertexIndex;
				if (color === null)
					color = this.color;
				if (color2 === null)
					color2 = this.color;
				if (color3 === null)
					color3 = this.color;
				if (filled) {
					this.vertex(x, y, color);
					this.vertex(x2, y2, color2);
					this.vertex(x3, y3, color3);
				}
				else {
					this.vertex(x, y, color);
					this.vertex(x2, y2, color2);
					this.vertex(x2, y2, color);
					this.vertex(x3, y3, color2);
					this.vertex(x3, y3, color);
					this.vertex(x, y, color2);
				}
			};
			ShapeRenderer.prototype.quad = function (filled, x, y, x2, y2, x3, y3, x4, y4, color, color2, color3, color4) {
				if (color === void 0) { color = null; }
				if (color2 === void 0) { color2 = null; }
				if (color3 === void 0) { color3 = null; }
				if (color4 === void 0) { color4 = null; }
				this.check(filled ? ShapeType.Filled : ShapeType.Line, 3);
				var vertices = this.mesh.getVertices();
				var idx = this.vertexIndex;
				if (color === null)
					color = this.color;
				if (color2 === null)
					color2 = this.color;
				if (color3 === null)
					color3 = this.color;
				if (color4 === null)
					color4 = this.color;
				if (filled) {
					this.vertex(x, y, color);
					this.vertex(x2, y2, color2);
					this.vertex(x3, y3, color3);
					this.vertex(x3, y3, color3);
					this.vertex(x4, y4, color4);
					this.vertex(x, y, color);
				}
				else {
					this.vertex(x, y, color);
					this.vertex(x2, y2, color2);
					this.vertex(x2, y2, color2);
					this.vertex(x3, y3, color3);
					this.vertex(x3, y3, color3);
					this.vertex(x4, y4, color4);
					this.vertex(x4, y4, color4);
					this.vertex(x, y, color);
				}
			};
			ShapeRenderer.prototype.rect = function (filled, x, y, width, height, color) {
				if (color === void 0) { color = null; }
				this.quad(filled, x, y, x + width, y, x + width, y + height, x, y + height, color, color, color, color);
			};
			ShapeRenderer.prototype.rectLine = function (filled, x1, y1, x2, y2, width, color) {
				if (color === void 0) { color = null; }
				this.check(filled ? ShapeType.Filled : ShapeType.Line, 8);
				if (color === null)
					color = this.color;
				var t = this.tmp.set(y2 - y1, x1 - x2);
				t.normalize();
				width *= 0.5;
				var tx = t.x * width;
				var ty = t.y * width;
				if (!filled) {
					this.vertex(x1 + tx, y1 + ty, color);
					this.vertex(x1 - tx, y1 - ty, color);
					this.vertex(x2 + tx, y2 + ty, color);
					this.vertex(x2 - tx, y2 - ty, color);
					this.vertex(x2 + tx, y2 + ty, color);
					this.vertex(x1 + tx, y1 + ty, color);
					this.vertex(x2 - tx, y2 - ty, color);
					this.vertex(x1 - tx, y1 - ty, color);
				}
				else {
					this.vertex(x1 + tx, y1 + ty, color);
					this.vertex(x1 - tx, y1 - ty, color);
					this.vertex(x2 + tx, y2 + ty, color);
					this.vertex(x2 - tx, y2 - ty, color);
					this.vertex(x2 + tx, y2 + ty, color);
					this.vertex(x1 - tx, y1 - ty, color);
				}
			};
			ShapeRenderer.prototype.x = function (x, y, size) {
				this.line(x - size, y - size, x + size, y + size);
				this.line(x - size, y + size, x + size, y - size);
			};
			ShapeRenderer.prototype.polygon = function (polygonVertices, offset, count, color) {
				if (color === void 0) { color = null; }
				if (count < 3)
					throw new Error("Polygon must contain at least 3 vertices");
				this.check(ShapeType.Line, count * 2);
				if (color === null)
					color = this.color;
				var vertices = this.mesh.getVertices();
				var idx = this.vertexIndex;
				offset <<= 1;
				count <<= 1;
				var firstX = polygonVertices[offset];
				var firstY = polygonVertices[offset + 1];
				var last = offset + count;
				for (var i = offset, n = offset + count - 2; i < n; i += 2) {
					var x1 = polygonVertices[i];
					var y1 = polygonVertices[i + 1];
					var x2 = 0;
					var y2 = 0;
					if (i + 2 >= last) {
						x2 = firstX;
						y2 = firstY;
					}
					else {
						x2 = polygonVertices[i + 2];
						y2 = polygonVertices[i + 3];
					}
					this.vertex(x1, y1, color);
					this.vertex(x2, y2, color);
				}
			};
			ShapeRenderer.prototype.circle = function (filled, x, y, radius, color, segments) {
				if (color === void 0) { color = null; }
				if (segments === void 0) { segments = 0; }
				if (segments === 0)
					segments = Math.max(1, (6 * spine.MathUtils.cbrt(radius)) | 0);
				if (segments <= 0)
					throw new Error("segments must be > 0.");
				if (color === null)
					color = this.color;
				var angle = 2 * spine.MathUtils.PI / segments;
				var cos = Math.cos(angle);
				var sin = Math.sin(angle);
				var cx = radius, cy = 0;
				if (!filled) {
					this.check(ShapeType.Line, segments * 2 + 2);
					for (var i = 0; i < segments; i++) {
						this.vertex(x + cx, y + cy, color);
						var temp_1 = cx;
						cx = cos * cx - sin * cy;
						cy = sin * temp_1 + cos * cy;
						this.vertex(x + cx, y + cy, color);
					}
					this.vertex(x + cx, y + cy, color);
				}
				else {
					this.check(ShapeType.Filled, segments * 3 + 3);
					segments--;
					for (var i = 0; i < segments; i++) {
						this.vertex(x, y, color);
						this.vertex(x + cx, y + cy, color);
						var temp_2 = cx;
						cx = cos * cx - sin * cy;
						cy = sin * temp_2 + cos * cy;
						this.vertex(x + cx, y + cy, color);
					}
					this.vertex(x, y, color);
					this.vertex(x + cx, y + cy, color);
				}
				var temp = cx;
				cx = radius;
				cy = 0;
				this.vertex(x + cx, y + cy, color);
			};
			ShapeRenderer.prototype.curve = function (x1, y1, cx1, cy1, cx2, cy2, x2, y2, segments, color) {
				if (color === void 0) { color = null; }
				this.check(ShapeType.Line, segments * 2 + 2);
				if (color === null)
					color = this.color;
				var subdiv_step = 1 / segments;
				var subdiv_step2 = subdiv_step * subdiv_step;
				var subdiv_step3 = subdiv_step * subdiv_step * subdiv_step;
				var pre1 = 3 * subdiv_step;
				var pre2 = 3 * subdiv_step2;
				var pre4 = 6 * subdiv_step2;
				var pre5 = 6 * subdiv_step3;
				var tmp1x = x1 - cx1 * 2 + cx2;
				var tmp1y = y1 - cy1 * 2 + cy2;
				var tmp2x = (cx1 - cx2) * 3 - x1 + x2;
				var tmp2y = (cy1 - cy2) * 3 - y1 + y2;
				var fx = x1;
				var fy = y1;
				var dfx = (cx1 - x1) * pre1 + tmp1x * pre2 + tmp2x * subdiv_step3;
				var dfy = (cy1 - y1) * pre1 + tmp1y * pre2 + tmp2y * subdiv_step3;
				var ddfx = tmp1x * pre4 + tmp2x * pre5;
				var ddfy = tmp1y * pre4 + tmp2y * pre5;
				var dddfx = tmp2x * pre5;
				var dddfy = tmp2y * pre5;
				while (segments-- > 0) {
					this.vertex(fx, fy, color);
					fx += dfx;
					fy += dfy;
					dfx += ddfx;
					dfy += ddfy;
					ddfx += dddfx;
					ddfy += dddfy;
					this.vertex(fx, fy, color);
				}
				this.vertex(fx, fy, color);
				this.vertex(x2, y2, color);
			};
			ShapeRenderer.prototype.vertex = function (x, y, color) {
				var idx = this.vertexIndex;
				var vertices = this.mesh.getVertices();
				vertices[idx++] = x;
				vertices[idx++] = y;
				vertices[idx++] = color.r;
				vertices[idx++] = color.g;
				vertices[idx++] = color.b;
				vertices[idx++] = color.a;
				this.vertexIndex = idx;
			};
			ShapeRenderer.prototype.end = function () {
				if (!this.isDrawing)
					throw new Error("ShapeRenderer.begin() has not been called");
				this.flush();
				this.context.gl.disable(this.context.gl.BLEND);
				this.isDrawing = false;
			};
			ShapeRenderer.prototype.flush = function () {
				if (this.vertexIndex == 0)
					return;
				this.mesh.setVerticesLength(this.vertexIndex);
				this.mesh.draw(this.shader, this.shapeType);
				this.vertexIndex = 0;
			};
			ShapeRenderer.prototype.check = function (shapeType, numVertices) {
				if (!this.isDrawing)
					throw new Error("ShapeRenderer.begin() has not been called");
				if (this.shapeType == shapeType) {
					if (this.mesh.maxVertices() - this.mesh.numVertices() < numVertices)
						this.flush();
					else
						return;
				}
				else {
					this.flush();
					this.shapeType = shapeType;
				}
			};
			ShapeRenderer.prototype.dispose = function () {
				this.mesh.dispose();
			};
			return ShapeRenderer;
		}());
		webgl.ShapeRenderer = ShapeRenderer;
		var ShapeType;
		(function (ShapeType) {
			ShapeType[ShapeType["Point"] = 0] = "Point";
			ShapeType[ShapeType["Line"] = 1] = "Line";
			ShapeType[ShapeType["Filled"] = 4] = "Filled";
		})(ShapeType = webgl.ShapeType || (webgl.ShapeType = {}));
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var SkeletonDebugRenderer = (function () {
			function SkeletonDebugRenderer(context) {
				this.boneLineColor = new spine.Color(1, 0, 0, 1);
				this.boneOriginColor = new spine.Color(0, 1, 0, 1);
				this.attachmentLineColor = new spine.Color(0, 0, 1, 0.5);
				this.triangleLineColor = new spine.Color(1, 0.64, 0, 0.5);
				this.pathColor = new spine.Color().setFromString("FF7F00");
				this.clipColor = new spine.Color(0.8, 0, 0, 2);
				this.aabbColor = new spine.Color(0, 1, 0, 0.5);
				this.drawBones = true;
				this.drawRegionAttachments = true;
				this.drawBoundingBoxes = true;
				this.drawMeshHull = true;
				this.drawMeshTriangles = true;
				this.drawPaths = true;
				this.drawSkeletonXY = false;
				this.drawClipping = true;
				this.premultipliedAlpha = false;
				this.scale = 1;
				this.boneWidth = 2;
				this.bounds = new spine.SkeletonBounds();
				this.temp = new Array();
				this.vertices = spine.Utils.newFloatArray(2 * 1024);
				this.context = context instanceof webgl.ManagedWebGLRenderingContext ? context : new webgl.ManagedWebGLRenderingContext(context);
			}
			SkeletonDebugRenderer.prototype.draw = function (shapes, skeleton, ignoredBones) {
				if (ignoredBones === void 0) { ignoredBones = null; }
				var skeletonX = skeleton.x;
				var skeletonY = skeleton.y;
				var gl = this.context.gl;
				var srcFunc = this.premultipliedAlpha ? gl.ONE : gl.SRC_ALPHA;
				shapes.setBlendMode(srcFunc, gl.ONE_MINUS_SRC_ALPHA);
				var bones = skeleton.bones;
				if (this.drawBones) {
					shapes.setColor(this.boneLineColor);
					for (var i = 0, n = bones.length; i < n; i++) {
						var bone = bones[i];
						if (ignoredBones && ignoredBones.indexOf(bone.data.name) > -1)
							continue;
						if (bone.parent == null)
							continue;
						var x = skeletonX + bone.data.length * bone.a + bone.worldX;
						var y = skeletonY + bone.data.length * bone.c + bone.worldY;
						shapes.rectLine(true, skeletonX + bone.worldX, skeletonY + bone.worldY, x, y, this.boneWidth * this.scale);
					}
					if (this.drawSkeletonXY)
						shapes.x(skeletonX, skeletonY, 4 * this.scale);
				}
				if (this.drawRegionAttachments) {
					shapes.setColor(this.attachmentLineColor);
					var slots = skeleton.slots;
					for (var i = 0, n = slots.length; i < n; i++) {
						var slot = slots[i];
						var attachment = slot.getAttachment();
						if (attachment instanceof spine.RegionAttachment) {
							var regionAttachment = attachment;
							var vertices = this.vertices;
							regionAttachment.computeWorldVertices(slot.bone, vertices, 0, 2);
							shapes.line(vertices[0], vertices[1], vertices[2], vertices[3]);
							shapes.line(vertices[2], vertices[3], vertices[4], vertices[5]);
							shapes.line(vertices[4], vertices[5], vertices[6], vertices[7]);
							shapes.line(vertices[6], vertices[7], vertices[0], vertices[1]);
						}
					}
				}
				if (this.drawMeshHull || this.drawMeshTriangles) {
					var slots = skeleton.slots;
					for (var i = 0, n = slots.length; i < n; i++) {
						var slot = slots[i];
						if (!slot.bone.active)
							continue;
						var attachment = slot.getAttachment();
						if (!(attachment instanceof spine.MeshAttachment))
							continue;
						var mesh = attachment;
						var vertices = this.vertices;
						mesh.computeWorldVertices(slot, 0, mesh.worldVerticesLength, vertices, 0, 2);
						var triangles = mesh.triangles;
						var hullLength = mesh.hullLength;
						if (this.drawMeshTriangles) {
							shapes.setColor(this.triangleLineColor);
							for (var ii = 0, nn = triangles.length; ii < nn; ii += 3) {
								var v1 = triangles[ii] * 2, v2 = triangles[ii + 1] * 2, v3 = triangles[ii + 2] * 2;
								shapes.triangle(false, vertices[v1], vertices[v1 + 1], vertices[v2], vertices[v2 + 1], vertices[v3], vertices[v3 + 1]);
							}
						}
						if (this.drawMeshHull && hullLength > 0) {
							shapes.setColor(this.attachmentLineColor);
							hullLength = (hullLength >> 1) * 2;
							var lastX = vertices[hullLength - 2], lastY = vertices[hullLength - 1];
							for (var ii = 0, nn = hullLength; ii < nn; ii += 2) {
								var x = vertices[ii], y = vertices[ii + 1];
								shapes.line(x, y, lastX, lastY);
								lastX = x;
								lastY = y;
							}
						}
					}
				}
				if (this.drawBoundingBoxes) {
					var bounds = this.bounds;
					bounds.update(skeleton, true);
					shapes.setColor(this.aabbColor);
					shapes.rect(false, bounds.minX, bounds.minY, bounds.getWidth(), bounds.getHeight());
					var polygons = bounds.polygons;
					var boxes = bounds.boundingBoxes;
					for (var i = 0, n = polygons.length; i < n; i++) {
						var polygon = polygons[i];
						shapes.setColor(boxes[i].color);
						shapes.polygon(polygon, 0, polygon.length);
					}
				}
				if (this.drawPaths) {
					var slots = skeleton.slots;
					for (var i = 0, n = slots.length; i < n; i++) {
						var slot = slots[i];
						if (!slot.bone.active)
							continue;
						var attachment = slot.getAttachment();
						if (!(attachment instanceof spine.PathAttachment))
							continue;
						var path = attachment;
						var nn = path.worldVerticesLength;
						var world = this.temp = spine.Utils.setArraySize(this.temp, nn, 0);
						path.computeWorldVertices(slot, 0, nn, world, 0, 2);
						var color = this.pathColor;
						var x1 = world[2], y1 = world[3], x2 = 0, y2 = 0;
						if (path.closed) {
							shapes.setColor(color);
							var cx1 = world[0], cy1 = world[1], cx2 = world[nn - 2], cy2 = world[nn - 1];
							x2 = world[nn - 4];
							y2 = world[nn - 3];
							shapes.curve(x1, y1, cx1, cy1, cx2, cy2, x2, y2, 32);
							shapes.setColor(SkeletonDebugRenderer.LIGHT_GRAY);
							shapes.line(x1, y1, cx1, cy1);
							shapes.line(x2, y2, cx2, cy2);
						}
						nn -= 4;
						for (var ii = 4; ii < nn; ii += 6) {
							var cx1 = world[ii], cy1 = world[ii + 1], cx2 = world[ii + 2], cy2 = world[ii + 3];
							x2 = world[ii + 4];
							y2 = world[ii + 5];
							shapes.setColor(color);
							shapes.curve(x1, y1, cx1, cy1, cx2, cy2, x2, y2, 32);
							shapes.setColor(SkeletonDebugRenderer.LIGHT_GRAY);
							shapes.line(x1, y1, cx1, cy1);
							shapes.line(x2, y2, cx2, cy2);
							x1 = x2;
							y1 = y2;
						}
					}
				}
				if (this.drawBones) {
					shapes.setColor(this.boneOriginColor);
					for (var i = 0, n = bones.length; i < n; i++) {
						var bone = bones[i];
						if (ignoredBones && ignoredBones.indexOf(bone.data.name) > -1)
							continue;
						shapes.circle(true, skeletonX + bone.worldX, skeletonY + bone.worldY, 3 * this.scale, SkeletonDebugRenderer.GREEN, 8);
					}
				}
				if (this.drawClipping) {
					var slots = skeleton.slots;
					shapes.setColor(this.clipColor);
					for (var i = 0, n = slots.length; i < n; i++) {
						var slot = slots[i];
						if (!slot.bone.active)
							continue;
						var attachment = slot.getAttachment();
						if (!(attachment instanceof spine.ClippingAttachment))
							continue;
						var clip = attachment;
						var nn = clip.worldVerticesLength;
						var world = this.temp = spine.Utils.setArraySize(this.temp, nn, 0);
						clip.computeWorldVertices(slot, 0, nn, world, 0, 2);
						for (var i_21 = 0, n_3 = world.length; i_21 < n_3; i_21 += 2) {
							var x = world[i_21];
							var y = world[i_21 + 1];
							var x2 = world[(i_21 + 2) % world.length];
							var y2 = world[(i_21 + 3) % world.length];
							shapes.line(x, y, x2, y2);
						}
					}
				}
			};
			SkeletonDebugRenderer.prototype.dispose = function () {
			};
			SkeletonDebugRenderer.LIGHT_GRAY = new spine.Color(192 / 255, 192 / 255, 192 / 255, 1);
			SkeletonDebugRenderer.GREEN = new spine.Color(0, 1, 0, 1);
			return SkeletonDebugRenderer;
		}());
		webgl.SkeletonDebugRenderer = SkeletonDebugRenderer;
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var Renderable = (function () {
			function Renderable(vertices, numVertices, numFloats) {
				this.vertices = vertices;
				this.numVertices = numVertices;
				this.numFloats = numFloats;
			}
			return Renderable;
		}());
		;
		var SkeletonRenderer = (function () {
			function SkeletonRenderer(context, twoColorTint) {
				if (twoColorTint === void 0) { twoColorTint = true; }
				this.premultipliedAlpha = false;
				this.vertexEffect = null;
				this.tempColor = new spine.Color();
				this.tempColor2 = new spine.Color();
				this.vertexSize = 2 + 2 + 4;
				this.twoColorTint = false;
				this.renderable = new Renderable(null, 0, 0);
				this.clipper = new spine.SkeletonClipping();
				this.temp = new spine.Vector2();
				this.temp2 = new spine.Vector2();
				this.temp3 = new spine.Color();
				this.temp4 = new spine.Color();
				this.twoColorTint = twoColorTint;
				if (twoColorTint)
					this.vertexSize += 4;
				this.vertices = spine.Utils.newFloatArray(this.vertexSize * 1024);
			}
			SkeletonRenderer.prototype.draw = function (batcher, skeleton, slotRangeStart, slotRangeEnd) {
				if (slotRangeStart === void 0) { slotRangeStart = -1; }
				if (slotRangeEnd === void 0) { slotRangeEnd = -1; }
				var clipper = this.clipper;
				var premultipliedAlpha = this.premultipliedAlpha;
				var twoColorTint = this.twoColorTint;
				var blendMode = null;
				var tempPos = this.temp;
				var tempUv = this.temp2;
				var tempLight = this.temp3;
				var tempDark = this.temp4;
				var renderable = this.renderable;
				var uvs = null;
				var triangles = null;
				var drawOrder = skeleton.drawOrder;
				var attachmentColor = null;
				var skeletonColor = skeleton.color;
				var vertexSize = twoColorTint ? 12 : 8;
				var inRange = false;
				if (slotRangeStart == -1)
					inRange = true;
				for (var i = 0, n = drawOrder.length; i < n; i++) {
					var clippedVertexSize = clipper.isClipping() ? 2 : vertexSize;
					var slot = drawOrder[i];
					if (!slot.bone.active) {
						clipper.clipEndWithSlot(slot);
						continue;
					}
					if (slotRangeStart >= 0 && slotRangeStart == slot.data.index) {
						inRange = true;
					}
					if (!inRange) {
						clipper.clipEndWithSlot(slot);
						continue;
					}
					if (slotRangeEnd >= 0 && slotRangeEnd == slot.data.index) {
						inRange = false;
					}
					var attachment = slot.getAttachment();
					var texture = null;
					if (attachment instanceof spine.RegionAttachment) {
						var region = attachment;
						renderable.vertices = this.vertices;
						renderable.numVertices = 4;
						renderable.numFloats = clippedVertexSize << 2;
						region.computeWorldVertices(slot.bone, renderable.vertices, 0, clippedVertexSize);
						triangles = SkeletonRenderer.QUAD_TRIANGLES;
						uvs = region.uvs;
						texture = region.region.renderObject.texture;
						attachmentColor = region.color;
					}
					else if (attachment instanceof spine.MeshAttachment) {
						var mesh = attachment;
						renderable.vertices = this.vertices;
						renderable.numVertices = (mesh.worldVerticesLength >> 1);
						renderable.numFloats = renderable.numVertices * clippedVertexSize;
						if (renderable.numFloats > renderable.vertices.length) {
							renderable.vertices = this.vertices = spine.Utils.newFloatArray(renderable.numFloats);
						}
						mesh.computeWorldVertices(slot, 0, mesh.worldVerticesLength, renderable.vertices, 0, clippedVertexSize);
						triangles = mesh.triangles;
						texture = mesh.region.renderObject.texture;
						uvs = mesh.uvs;
						attachmentColor = mesh.color;
					}
					else if (attachment instanceof spine.ClippingAttachment) {
						var clip = (attachment);
						clipper.clipStart(slot, clip);
						continue;
					}
					else {
						clipper.clipEndWithSlot(slot);
						continue;
					}
					if (texture != null) {
						var slotColor = slot.color;
						var finalColor = this.tempColor;
						finalColor.r = skeletonColor.r * slotColor.r * attachmentColor.r;
						finalColor.g = skeletonColor.g * slotColor.g * attachmentColor.g;
						finalColor.b = skeletonColor.b * slotColor.b * attachmentColor.b;
						finalColor.a = skeletonColor.a * slotColor.a * attachmentColor.a;
						if (premultipliedAlpha) {
							finalColor.r *= finalColor.a;
							finalColor.g *= finalColor.a;
							finalColor.b *= finalColor.a;
						}
						var darkColor = this.tempColor2;
						if (slot.darkColor == null)
							darkColor.set(0, 0, 0, 1.0);
						else {
							if (premultipliedAlpha) {
								darkColor.r = slot.darkColor.r * finalColor.a;
								darkColor.g = slot.darkColor.g * finalColor.a;
								darkColor.b = slot.darkColor.b * finalColor.a;
							}
							else {
								darkColor.setFromColor(slot.darkColor);
							}
							darkColor.a = premultipliedAlpha ? 1.0 : 0.0;
						}
						var slotBlendMode = slot.data.blendMode;
						if (slotBlendMode != blendMode) {
							blendMode = slotBlendMode;
							batcher.setBlendMode(webgl.WebGLBlendModeConverter.getSourceGLBlendMode(blendMode, premultipliedAlpha), webgl.WebGLBlendModeConverter.getDestGLBlendMode(blendMode));
						}
						if (clipper.isClipping()) {
							clipper.clipTriangles(renderable.vertices, renderable.numFloats, triangles, triangles.length, uvs, finalColor, darkColor, twoColorTint);
							var clippedVertices = new Float32Array(clipper.clippedVertices);
							var clippedTriangles = clipper.clippedTriangles;
							if (this.vertexEffect != null) {
								var vertexEffect = this.vertexEffect;
								var verts = clippedVertices;
								if (!twoColorTint) {
									for (var v = 0, n_4 = clippedVertices.length; v < n_4; v += vertexSize) {
										tempPos.x = verts[v];
										tempPos.y = verts[v + 1];
										tempLight.set(verts[v + 2], verts[v + 3], verts[v + 4], verts[v + 5]);
										tempUv.x = verts[v + 6];
										tempUv.y = verts[v + 7];
										tempDark.set(0, 0, 0, 0);
										vertexEffect.transform(tempPos, tempUv, tempLight, tempDark);
										verts[v] = tempPos.x;
										verts[v + 1] = tempPos.y;
										verts[v + 2] = tempLight.r;
										verts[v + 3] = tempLight.g;
										verts[v + 4] = tempLight.b;
										verts[v + 5] = tempLight.a;
										verts[v + 6] = tempUv.x;
										verts[v + 7] = tempUv.y;
									}
								}
								else {
									for (var v = 0, n_5 = clippedVertices.length; v < n_5; v += vertexSize) {
										tempPos.x = verts[v];
										tempPos.y = verts[v + 1];
										tempLight.set(verts[v + 2], verts[v + 3], verts[v + 4], verts[v + 5]);
										tempUv.x = verts[v + 6];
										tempUv.y = verts[v + 7];
										tempDark.set(verts[v + 8], verts[v + 9], verts[v + 10], verts[v + 11]);
										vertexEffect.transform(tempPos, tempUv, tempLight, tempDark);
										verts[v] = tempPos.x;
										verts[v + 1] = tempPos.y;
										verts[v + 2] = tempLight.r;
										verts[v + 3] = tempLight.g;
										verts[v + 4] = tempLight.b;
										verts[v + 5] = tempLight.a;
										verts[v + 6] = tempUv.x;
										verts[v + 7] = tempUv.y;
										verts[v + 8] = tempDark.r;
										verts[v + 9] = tempDark.g;
										verts[v + 10] = tempDark.b;
										verts[v + 11] = tempDark.a;
									}
								}
							}
							batcher.draw(texture, clippedVertices, clippedTriangles);
						}
						else {
							var verts = renderable.vertices;
							if (this.vertexEffect != null) {
								var vertexEffect = this.vertexEffect;
								if (!twoColorTint) {
									for (var v = 0, u = 0, n_6 = renderable.numFloats; v < n_6; v += vertexSize, u += 2) {
										tempPos.x = verts[v];
										tempPos.y = verts[v + 1];
										tempUv.x = uvs[u];
										tempUv.y = uvs[u + 1];
										tempLight.setFromColor(finalColor);
										tempDark.set(0, 0, 0, 0);
										vertexEffect.transform(tempPos, tempUv, tempLight, tempDark);
										verts[v] = tempPos.x;
										verts[v + 1] = tempPos.y;
										verts[v + 2] = tempLight.r;
										verts[v + 3] = tempLight.g;
										verts[v + 4] = tempLight.b;
										verts[v + 5] = tempLight.a;
										verts[v + 6] = tempUv.x;
										verts[v + 7] = tempUv.y;
									}
								}
								else {
									for (var v = 0, u = 0, n_7 = renderable.numFloats; v < n_7; v += vertexSize, u += 2) {
										tempPos.x = verts[v];
										tempPos.y = verts[v + 1];
										tempUv.x = uvs[u];
										tempUv.y = uvs[u + 1];
										tempLight.setFromColor(finalColor);
										tempDark.setFromColor(darkColor);
										vertexEffect.transform(tempPos, tempUv, tempLight, tempDark);
										verts[v] = tempPos.x;
										verts[v + 1] = tempPos.y;
										verts[v + 2] = tempLight.r;
										verts[v + 3] = tempLight.g;
										verts[v + 4] = tempLight.b;
										verts[v + 5] = tempLight.a;
										verts[v + 6] = tempUv.x;
										verts[v + 7] = tempUv.y;
										verts[v + 8] = tempDark.r;
										verts[v + 9] = tempDark.g;
										verts[v + 10] = tempDark.b;
										verts[v + 11] = tempDark.a;
									}
								}
							}
							else {
								if (!twoColorTint) {
									for (var v = 2, u = 0, n_8 = renderable.numFloats; v < n_8; v += vertexSize, u += 2) {
										verts[v] = finalColor.r;
										verts[v + 1] = finalColor.g;
										verts[v + 2] = finalColor.b;
										verts[v + 3] = finalColor.a;
										verts[v + 4] = uvs[u];
										verts[v + 5] = uvs[u + 1];
									}
								}
								else {
									for (var v = 2, u = 0, n_9 = renderable.numFloats; v < n_9; v += vertexSize, u += 2) {
										verts[v] = finalColor.r;
										verts[v + 1] = finalColor.g;
										verts[v + 2] = finalColor.b;
										verts[v + 3] = finalColor.a;
										verts[v + 4] = uvs[u];
										verts[v + 5] = uvs[u + 1];
										verts[v + 6] = darkColor.r;
										verts[v + 7] = darkColor.g;
										verts[v + 8] = darkColor.b;
										verts[v + 9] = darkColor.a;
									}
								}
							}
							var view = renderable.vertices.subarray(0, renderable.numFloats);
							batcher.draw(texture, view, triangles);
						}
					}
					clipper.clipEndWithSlot(slot);
				}
				clipper.clipEnd();
			};
			SkeletonRenderer.QUAD_TRIANGLES = [0, 1, 2, 2, 3, 0];
			return SkeletonRenderer;
		}());
		webgl.SkeletonRenderer = SkeletonRenderer;
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var Vector3 = (function () {
			function Vector3(x, y, z) {
				if (x === void 0) { x = 0; }
				if (y === void 0) { y = 0; }
				if (z === void 0) { z = 0; }
				this.x = 0;
				this.y = 0;
				this.z = 0;
				this.x = x;
				this.y = y;
				this.z = z;
			}
			Vector3.prototype.setFrom = function (v) {
				this.x = v.x;
				this.y = v.y;
				this.z = v.z;
				return this;
			};
			Vector3.prototype.set = function (x, y, z) {
				this.x = x;
				this.y = y;
				this.z = z;
				return this;
			};
			Vector3.prototype.add = function (v) {
				this.x += v.x;
				this.y += v.y;
				this.z += v.z;
				return this;
			};
			Vector3.prototype.sub = function (v) {
				this.x -= v.x;
				this.y -= v.y;
				this.z -= v.z;
				return this;
			};
			Vector3.prototype.scale = function (s) {
				this.x *= s;
				this.y *= s;
				this.z *= s;
				return this;
			};
			Vector3.prototype.normalize = function () {
				var len = this.length();
				if (len == 0)
					return this;
				len = 1 / len;
				this.x *= len;
				this.y *= len;
				this.z *= len;
				return this;
			};
			Vector3.prototype.cross = function (v) {
				return this.set(this.y * v.z - this.z * v.y, this.z * v.x - this.x * v.z, this.x * v.y - this.y * v.x);
			};
			Vector3.prototype.multiply = function (matrix) {
				var l_mat = matrix.values;
				return this.set(this.x * l_mat[webgl.M00] + this.y * l_mat[webgl.M01] + this.z * l_mat[webgl.M02] + l_mat[webgl.M03], this.x * l_mat[webgl.M10] + this.y * l_mat[webgl.M11] + this.z * l_mat[webgl.M12] + l_mat[webgl.M13], this.x * l_mat[webgl.M20] + this.y * l_mat[webgl.M21] + this.z * l_mat[webgl.M22] + l_mat[webgl.M23]);
			};
			Vector3.prototype.project = function (matrix) {
				var l_mat = matrix.values;
				var l_w = 1 / (this.x * l_mat[webgl.M30] + this.y * l_mat[webgl.M31] + this.z * l_mat[webgl.M32] + l_mat[webgl.M33]);
				return this.set((this.x * l_mat[webgl.M00] + this.y * l_mat[webgl.M01] + this.z * l_mat[webgl.M02] + l_mat[webgl.M03]) * l_w, (this.x * l_mat[webgl.M10] + this.y * l_mat[webgl.M11] + this.z * l_mat[webgl.M12] + l_mat[webgl.M13]) * l_w, (this.x * l_mat[webgl.M20] + this.y * l_mat[webgl.M21] + this.z * l_mat[webgl.M22] + l_mat[webgl.M23]) * l_w);
			};
			Vector3.prototype.dot = function (v) {
				return this.x * v.x + this.y * v.y + this.z * v.z;
			};
			Vector3.prototype.length = function () {
				return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
			};
			Vector3.prototype.distance = function (v) {
				var a = v.x - this.x;
				var b = v.y - this.y;
				var c = v.z - this.z;
				return Math.sqrt(a * a + b * b + c * c);
			};
			return Vector3;
		}());
		webgl.Vector3 = Vector3;
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
var spine;
(function (spine) {
	var webgl;
	(function (webgl) {
		var ManagedWebGLRenderingContext = (function () {
			function ManagedWebGLRenderingContext(canvasOrContext, contextConfig) {
				var _this = this;
				if (contextConfig === void 0) { contextConfig = { alpha: "true" }; }
				this.restorables = new Array();
				if (canvasOrContext instanceof HTMLCanvasElement) {
					var canvas = canvasOrContext;
					this.gl = (canvas.getContext("webgl2", contextConfig) || canvas.getContext("webgl", contextConfig));
					this.canvas = canvas;
					canvas.addEventListener("webglcontextlost", function (e) {
						var event = e;
						if (e) {
							e.preventDefault();
						}
					});
					canvas.addEventListener("webglcontextrestored", function (e) {
						for (var i = 0, n = _this.restorables.length; i < n; i++) {
							_this.restorables[i].restore();
						}
					});
				}
				else {
					this.gl = canvasOrContext;
					this.canvas = this.gl.canvas;
				}
			}
			ManagedWebGLRenderingContext.prototype.addRestorable = function (restorable) {
				this.restorables.push(restorable);
			};
			ManagedWebGLRenderingContext.prototype.removeRestorable = function (restorable) {
				var index = this.restorables.indexOf(restorable);
				if (index > -1)
					this.restorables.splice(index, 1);
			};
			return ManagedWebGLRenderingContext;
		}());
		webgl.ManagedWebGLRenderingContext = ManagedWebGLRenderingContext;
		var WebGLBlendModeConverter = (function () {
			function WebGLBlendModeConverter() {
			}
			WebGLBlendModeConverter.getDestGLBlendMode = function (blendMode) {
				switch (blendMode) {
					case spine.BlendMode.Normal: return WebGLBlendModeConverter.ONE_MINUS_SRC_ALPHA;
					case spine.BlendMode.Additive: return WebGLBlendModeConverter.ONE;
					case spine.BlendMode.Multiply: return WebGLBlendModeConverter.ONE_MINUS_SRC_ALPHA;
					case spine.BlendMode.Screen: return WebGLBlendModeConverter.ONE_MINUS_SRC_ALPHA;
					default: throw new Error("Unknown blend mode: " + blendMode);
				}
			};
			WebGLBlendModeConverter.getSourceGLBlendMode = function (blendMode, premultipliedAlpha) {
				if (premultipliedAlpha === void 0) { premultipliedAlpha = false; }
				switch (blendMode) {
					case spine.BlendMode.Normal: return premultipliedAlpha ? WebGLBlendModeConverter.ONE : WebGLBlendModeConverter.SRC_ALPHA;
					case spine.BlendMode.Additive: return premultipliedAlpha ? WebGLBlendModeConverter.ONE : WebGLBlendModeConverter.SRC_ALPHA;
					case spine.BlendMode.Multiply: return WebGLBlendModeConverter.DST_COLOR;
					case spine.BlendMode.Screen: return WebGLBlendModeConverter.ONE;
					default: throw new Error("Unknown blend mode: " + blendMode);
				}
			};
			WebGLBlendModeConverter.ZERO = 0;
			WebGLBlendModeConverter.ONE = 1;
			WebGLBlendModeConverter.SRC_COLOR = 0x0300;
			WebGLBlendModeConverter.ONE_MINUS_SRC_COLOR = 0x0301;
			WebGLBlendModeConverter.SRC_ALPHA = 0x0302;
			WebGLBlendModeConverter.ONE_MINUS_SRC_ALPHA = 0x0303;
			WebGLBlendModeConverter.DST_ALPHA = 0x0304;
			WebGLBlendModeConverter.ONE_MINUS_DST_ALPHA = 0x0305;
			WebGLBlendModeConverter.DST_COLOR = 0x0306;
			return WebGLBlendModeConverter;
		}());
		webgl.WebGLBlendModeConverter = WebGLBlendModeConverter;
	})(webgl = spine.webgl || (spine.webgl = {}));
})(spine || (spine = {}));
//# sourceMappingURL=spine-webgl.js.map