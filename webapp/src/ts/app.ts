const LETTERS = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 
    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#', '?'
] as const;

interface GameState {
    valid: boolean;
    letter_limits: Record<typeof LETTERS[number], number>;
    categories: Record<typeof LETTERS[number], number>;
}

// Initial game state
export function gameState() {

    const state: GameState = {
        valid: true,
        letter_limits: Object.fromEntries(
            LETTERS.map(letter => [letter, 6])
        ) as Record<typeof LETTERS[number], number>,
        categories: Object.fromEntries(
            LETTERS.map(letter => [letter, 0])
        ) as Record<typeof LETTERS[number], number>
    }

    return {
        ...state,

        mapLetterLimits(letter_limits_list: number[]): void {
            for (let i = 0; i < letter_limits_list.length; i++){
                this.letter_limits[LETTERS[i]] = letter_limits_list[i];
            }
        }
    }
}
