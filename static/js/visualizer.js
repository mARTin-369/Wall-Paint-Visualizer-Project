const detect = document.getElementById("detect");
const paint = document.getElementById("paint");
const colorPicker = document.getElementById("color-picker");
const imageCanvas = document.getElementById("img-canvas");
const download = document.getElementById("download");
const loader = document.getElementById("loader");

imageCanvas.onload = () => {
  unsetLoading();
};

const setLoading = () => {
  imageCanvas.style.opacity = 0.5;
  loader.style.display = "inline";
};

const unsetLoading = () => {
  imageCanvas.style.opacity = 1.0;
  loader.style.display = "none";
};

detect.addEventListener("click", async () => {
  setLoading();

  const { data } = await axios.get(`${window.location.href}/detect`);
  const image = data.image;

  // console.log(data)
  imageCanvas.src = image;
  download.href = image;

  // unsetLoading()
});

paint.addEventListener("click", async () => {
  setLoading();

  const { data } = await axios.get(`${window.location.href}/paint`);
  const image = `${data.image}?id=${performance.now()}`;

  // console.log(data)
  imageCanvas.src = image;
  download.href = image;

  // unsetLoading()
});

colorPicker.addEventListener("change", async (e) => {
  setLoading();

  const { data } = await axios.post(`${window.location.href}/detect`, {
    colour: e.target.value,
  });
  const image = `${data.image}?id=${performance.now()}`;

  // console.log(data)
  imageCanvas.src = image;
  download.href = image;

  // unsetLoading()
});

const handleColorClick = async (color) => {
  setLoading();

  const { data } = await axios.post(`${window.location.href}/detect`, {
    colour: color,
  });
  const image = `${data.image}?id=${performance.now()}`;

  // console.log(data)
  imageCanvas.src = image;
  download.href = image;

  // unsetLoading()
};

const colorThief = new ColorThief();
const imgPalette = document.querySelector("#img-pallete");
const paletteGrid = document.querySelector("#palette-grid");

function rgbToHex(rgb) {
  return (
    "#" +
    ((1 << 24) + (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]).toString(16).slice(1)
  );
}

imgPalette.style.display = "none";
imgPalette.onload = () => {
  const palette = colorThief.getPalette(imgPalette, 16);
  var content = "";
  palette.forEach((color) => {
    const hex = rgbToHex(color);
    content += `
		<div class="col">
			<div class="card" onclick="handleColorClick('${hex}')">
				<div class="color-display" style="background-color: ${hex};" data-value="${hex}"></div>
				<div class="card-body color-box">
					<h6 class="card-title color-value">${hex}</h6>
				</div>
			</div>
		</div>
	`;
  });
  paletteGrid.innerHTML = content;
};

function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      imgPalette.style.display = "block";
      imgPalette.src = e.target.result;
    };

    reader.readAsDataURL(input.files[0]);
  }
}
