// Получаем HTML-элемент <canvas> по ID "canvas"
const canvas = document.getElementById('canvas');

// Получаем 2D-контекст — объект для рисования в canvas
const ctx = canvas.getContext('2d');

// Размер одного тайла (пикселя карты) в пикселях экрана
const tileSize = 8;



// -------------------------------------------------------------
//                 ОПРЕДЕЛЕНИЕ ДОСТУПНЫХ ТАЙЛОВ
// -------------------------------------------------------------

// Массив тайлов, каждый тайл имеет id и цвет.
// В будущем вместо цветов можно вставить изображения.
const tiles = [
  {id: 0, color: 'white'},  // id=0 → пустота
  {id: 1, color: 'green'},  // id=1 → трава
  {id: 2, color: 'brown'},  // id=2 → земля
  {id: 3, color: 'blue'},   // id=3 → вода
  {id: 4, color: 'gray'}    // id=4 → камень
];

// ID тайла, который выбран для рисования
let selectedTile = 1;



// -------------------------------------------------------------
//                ПАРАМЕТРЫ И ДАННЫЕ КАРТЫ
// -------------------------------------------------------------

// Главная переменная, где хранится вся карта (2D массив)
let map = [];

// Ширина карты (в тайлах)
let mapWidth = 100;

// Высота карты (в тайлах)
let mapHeight = 60;



// -------------------------------------------------------------
//           ФУНКЦИЯ: СОЗДАНИЕ ПУСТОЙ КАРТЫ
// -------------------------------------------------------------

// Создаёт карту width×height, заполненную ID 0 (пусто)
function createEmptyMap(width, height) {
  // Создаёт массив высотой height,
  // внутри каждый элемент — массив шириной width из нулей
  return Array.from({length: height}, () =>
    Array(width).fill(0)
  );
}



// -------------------------------------------------------------
//            ФУНКЦИЯ: ГЕНЕРАЦИЯ ПРИМЕРНОЙ КАРТЫ
// -------------------------------------------------------------

function createExampleMap(width, height) {

  // Создаём 2D-массив
  return Array.from({length: height}, (_, y) => 
    Array.from({length: width}, (_, x) => {

      // 1. Каменные границы вокруг всей карты
      if (y === 0 || y === height-1 || x === 0 || x === width-1)
        return 4; // камень

      // 2. Прямоугольник земли в средней области
      if (y > 20 && y < 25 && x > 30 && x < 70)
        return 2; // земля

      // 3. Немного "случайной" воды
      if ((x + y) % 10 === 0)
        return 3; // вода

      // 4. Всё остальное — трава
      return 1;
    })
  );
}



// -------------------------------------------------------------
//      ФУНКЦИЯ: УСТАНОВИТЬ КАРТУ ДЛЯ ОТОБРАЖЕНИЯ
// -------------------------------------------------------------

function setMap(matrix) {

  // Сохраняем размеры карты
  mapHeight = matrix.length;
  mapWidth = matrix[0].length;

  // Копируем матрицу (чтобы не менять её напрямую)
  map = matrix.map(row => [...row]);

  // Меняем размер canvas под реальные размеры карты
  canvas.width = mapWidth * tileSize;
  canvas.height = mapHeight * tileSize;

  // Отрисовываем карту
  drawMap();
}



// -------------------------------------------------------------
//                 СОЗДАНИЕ ПАЛИТРЫ ТАЙЛОВ
// -------------------------------------------------------------

// Получаем div, куда будем вставлять элементы палитры
const paletteDiv = document.getElementById('palette');

// Генерация кнопок тайлов
tiles.forEach(tile => {

  // Создаём HTML-элемент div — квадрат 16×16
  const tileDiv = document.createElement('div');

  // Добавляем класс стилей .tile
  tileDiv.classList.add('tile');

  // Красим div в цвет тайла
  tileDiv.style.background = tile.color;

  // При клике выбираем этот тайл
  tileDiv.addEventListener('click', () => {

    // Запоминаем его ID, чтобы рисовать этим цветом
    selectedTile = tile.id;

    // Убираем выделение со всех тайлов
    document.querySelectorAll('.tile').forEach(t =>
      t.classList.remove('selected')
    );

    // Выделяем текущий
    tileDiv.classList.add('selected');
  });

  // Отмечаем выбранный по умолчанию
  if (tile.id === selectedTile) tileDiv.classList.add('selected');

  // Добавляем тайл в палитру
  paletteDiv.appendChild(tileDiv);
});



// -------------------------------------------------------------
//                 ОТРИСОВКА ВСЕЙ КАРТЫ
// -------------------------------------------------------------

function drawMap() {

  // Очищаем canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Проходим по каждому тайлу карты
  for (let y = 0; y < mapHeight; y++) {
    for (let x = 0; x < mapWidth; x++) {

      // Получаем объект тайла по его ID
      const tile = tiles[map[y][x]] || tiles[0];

      // Устанавливаем цвет
      ctx.fillStyle = tile.color;

      // Рисуем квадрат (тайл)
      ctx.fillRect(
        x * tileSize,
        y * tileSize,
        tileSize,
        tileSize
      );
    }
  }
}



// -------------------------------------------------------------
//            ВЗАИМОДЕЙСТВИЕ С МЫШЬЮ — РИСОВАНИЕ
// -------------------------------------------------------------

let isDrawing = false;

// Когда нажата кнопка мыши → начать рисовать
canvas.addEventListener('mousedown', e => {
  isDrawing = true;
  drawTile(e); // рисуем сразу в момент клика
});

// Когда отпускаем кнопку мыши → перестать рисовать
canvas.addEventListener('mouseup', () => {
  isDrawing = false;
});

// Если ушли курсором с canvas → перестать рисовать
canvas.addEventListener('mouseleave', () => {
  isDrawing = false;
});

// Движение мыши → рисуем, только если зажата кнопка
canvas.addEventListener('mousemove', e => {
  if (isDrawing) drawTile(e);
});



// -------------------------------------------------------------
//          ФУНКЦИЯ: ИЗМЕНИТЬ КОНКРЕТНЫЙ ТАЙЛ
// -------------------------------------------------------------

function drawTile(e) {

  // Получаем координаты canvas на странице
  const rect = canvas.getBoundingClientRect();

  // Вычисляем координаты тайла, по которому кликнули
  const x = Math.floor((e.clientX - rect.left) / tileSize);
  const y = Math.floor((e.clientY - rect.top) / tileSize);

  // Проверяем, попали ли в карту
  if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight) {

    // Меняем значение в матрице
    map[y][x] = selectedTile;

    // Перерисовываем всю карту
    drawMap();
  }
}



// -------------------------------------------------------------
//      ФУНКЦИЯ: ВЕРНУТЬ ТЕКУЩУЮ МАТРИЦУ (копию)
// -------------------------------------------------------------

function getMap() {
  // Возвращаем новую копию массива, чтобы не ломали оригинал
  return map.map(row => [...row]);
}



// -------------------------------------------------------------
//        ИНИЦИАЛИЗАЦИЯ: ЗАГРУЗКА ПРИМЕРНОЙ КАРТЫ
// -------------------------------------------------------------

setMap(createExampleMap(mapWidth, mapHeight));



// -------------------------------------------------------------
//              СОХРАНЕНИЕ КАРТЫ В БАЗУ ЧЕРЕЗ API
// -------------------------------------------------------------

document.getElementById('saveBtn').addEventListener('click', async () => {

  // Получаем текущую карту как 2D-массив
  const matrix = getMap();

  // Спрашиваем у пользователя название карты
  const mapName = prompt("Введите название карты:");

  // Если пусто — не сохраняем
  if (!mapName) {
    alert("Название обязательно!");
    return;
  }

  try {

    // Отправляем POST-запрос на backend FastAPI
    const response = await fetch("http://localhost:8000/map/add_map/", {
      method: "POST",

      // Заголовки
      headers: {
        "Content-Type": "application/json",

        // JWT токен авторизации (если используется)
        "Authorization": "Bearer " + localStorage.getItem("token")
      },

      // Содержимое запроса — JSON с именем и матрицей
      body: JSON.stringify({
        map_name: mapName,
        matrix: matrix
      })
    });

    // Если сервер вернул ошибку
    if (!response.ok) {
      throw new Error("Ошибка сохранения");
    }

    // Если всё ок — выводим сообщение
    alert("Карта сохранена!");

  } catch (error) {
    console.error(error);
    alert("Не удалось сохранить карту");
  }
});