import "./css/style.css";
import "./css/normalize.css";
import Alpine from "alpinejs";
import { Game } from "./ts/game";
import { Telegram } from "./ts/telegram";

window.Alpine = Alpine;
Alpine.data("Game", Game);
Alpine.data("Telegram", Telegram);
Alpine.start();
