import { category, LETTERS } from "./constants";

function normalizeText(text: string) {
	return text
		.toLowerCase()
		.replaceAll("ñ", "\x01")
		.normalize("NFD")
		.replace(/[\u0300-\u036f]/g, "")
		.replaceAll("\x01", "ñ");
}

function frequencyText(category: category, count: number, limit: number) {
	if (count > limit) {
		return `${category} | ${count.toString().padEnd(limit, " ")}`;
	}
	const bars = "■".repeat(count);
	const spaces = "□".repeat(limit - count);
	return `${category} | ${bars}${spaces}`;
}

interface GameState {
	valid: boolean;
	letterLimits: Record<category, number>;
	categories: Record<category, number>;
}

export function Game() {
	const state: GameState = {
		valid: true,
		letterLimits: Object.fromEntries(
			LETTERS.map((letter) => [letter, 6])
		) as Record<category, number>,
		categories: Object.fromEntries(
			LETTERS.map((letter) => [letter, 0])
		) as Record<category, number>,
	};

	console.log(state.categories);

	return {
		...state,

		mapLetterLimits(letterLimits: number[]): void {
			for (let i = 0; i < letterLimits.length; i++) {
				this.letterLimits[LETTERS[i]] = letterLimits[i];
			}
		},

		categoryLimit(category: category) {
			return this.letterLimits[category];
		},

		getFrequencyClass(category: category, count: number) {
			if (count > this.letterLimits[category]) return "tx";
			return `t${count}`;
		},

		getOtherFrequencyClass(category: category, count: number) {
			if (count > this.letterLimits[category]) return "fx";
			return `f${count}`;
		},

		characterCategory(char: string): category {
			if (this.categories.hasOwnProperty(char)) {
				return char as category;
			} else if (!isNaN(Number(char))) {
				return "#";
			} else if (/[^a-z0-9]/.test(char)) {
				return "?";
			}

			throw new Error("Unidentified character");
		},

		getCharClass(char: string) {
			const normalizedChar = normalizeText(char);
			const category = this.characterCategory(normalizedChar);
			const count = this.categories[category];
			return this.getFrequencyClass(
				this.characterCategory(normalizedChar),
				count
			);
		},

		checkValid(text: string) {
			for (let char of text) {
				if (this.getCharClass(char) == "tx") {
					return false;
				}
			}
			return true;
		},

		normalizeText,
		frequencyText,
	};
}
