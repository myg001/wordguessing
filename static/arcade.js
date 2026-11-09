const difficultyOrder = ['easy', 'medium', 'hard'];
const screenElements = {
    welcome: document.querySelector('#welcome-screen'),
    stages: document.querySelector('#stages-screen'),
    difficulty: document.querySelector('#difficulty-screen'),
    playing: document.querySelector('#playing-screen'),
};
const nameDialog = document.querySelector('#name-dialog');
const nameInput = document.querySelector('#name-input');
const nameError = document.querySelector('#name-error');
const answerOptions = document.querySelector('#answer-options');
const feedback = document.querySelector('#feedback');
const hintButton = document.querySelector('#hint-button');
let currentState = null;
let toastTimeout = null;
let questionBanks = null;
let player = null;

function makeNewPlayer(name = '') {
    return {
        name,
        screen: name ? 'stages' : 'welcome',
        score: 0,
        unlocked_stage: name ? 1 : 0,
        completed_stages: [],
        stage: null,
        difficulty: null,
        stage_difficulties: {},
        round: 0,
        seen_questions: Object.fromEntries(difficultyOrder.map((key) => [key, []])),
        game: null,
    };
}

function savePlayer() {
    try {
        localStorage.setItem('byte-buddy-pages-v1', JSON.stringify(player));
    } catch {
        showToast('บันทึกความคืบหน้าไม่ได้ โปรดตรวจพื้นที่จัดเก็บของเบราว์เซอร์');
    }
}

function buildViewState() {
    const state = {
        screen: player.screen,
        player_name: player.name,
        score: player.score,
        unlocked_stage: player.unlocked_stage,
        completed_stages: player.completed_stages,
        total_stages: 10,
        selected_stage: player.stage,
        difficulty: player.difficulty,
        difficulties: Object.fromEntries(difficultyOrder.map((key) => [key, {
            label: questionBanks[key].label,
            description: questionBanks[key].description,
        }])),
        difficulty_counts: Object.fromEntries(difficultyOrder.map((key) => [key, questionBanks[key].questions.length])),
        round: player.round,
    };
    if (player.game) {
        Object.assign(state, {
            ...player.game,
            score: player.score,
            answer: player.game.status === 'playing' ? null : player.game.answer.toUpperCase(),
            correct_choice: player.game.status === 'playing' ? null : player.game.correct_choice,
        });
    }
    return state;
}

function createRound(difficulty) {
    const bank = questionBanks[difficulty].questions;
    const seen = player.seen_questions[difficulty];
    let available = bank.filter((question) => !seen.includes(question.id));
    if (available.length === 0) {
        seen.length = 0;
        available = [...bank];
    }
    const question = available[Math.floor(Math.random() * available.length)];
    seen.push(question.id);
    const distractors = bank.filter((item) => item.id !== question.id);
    for (let index = distractors.length - 1; index > 0; index -= 1) {
        const swapIndex = Math.floor(Math.random() * (index + 1));
        [distractors[index], distractors[swapIndex]] = [distractors[swapIndex], distractors[index]];
    }
    const options = [question, ...distractors.slice(0, 3)];
    for (let index = options.length - 1; index > 0; index -= 1) {
        const swapIndex = Math.floor(Math.random() * (index + 1));
        [options[index], options[swapIndex]] = [options[swapIndex], options[index]];
    }
    const choices = options.map((option, index) => ({
        letter: String.fromCharCode(65 + index),
        text: option.answer,
    }));
    return {
        question_id: question.id,
        answer: question.answer,
        category: question.category,
        question: question.question,
        clue: question.clue,
        choices,
        correct_choice: choices[options.findIndex((option) => option.id === question.id)].letter,
        selected_choice: null,
        hints: [],
        all_hints: question.hints,
        revealed_hints: 0,
        hints_remaining: question.hints.length,
        status: 'playing',
        message: 'เลือกคำตอบที่ถูกต้องจากตัวเลือกด้านล่าง',
    };
}

function beginLevel(difficulty) {
    if (!player.stage || !questionBanks[difficulty]) throw new Error('เลือกระดับความยากก่อนเริ่มเล่นนะ');
    player.difficulty = difficulty;
    player.stage_difficulties[player.stage] = difficulty;
    player.round += 1;
    player.game = createRound(difficulty);
    player.screen = 'playing';
}

function requestJson(url, payload = {}) {
    switch (url) {
        case '/api/start':
            player = makeNewPlayer(payload.name);
            break;
        case '/api/select-stage':
            if (payload.stage > player.unlocked_stage) throw new Error('ผ่านด่านก่อนหน้าเพื่อปลดล็อกด่านนี้ก่อนนะ');
            player.stage = payload.stage;
            player.game = null;
            if (player.stage_difficulties[payload.stage]) {
                beginLevel(player.stage_difficulties[payload.stage]);
            } else {
                player.difficulty = null;
                player.screen = 'difficulty';
            }
            break;
        case '/api/start-level':
            beginLevel(payload.difficulty);
            break;
        case '/api/return-to-stages':
            player.screen = 'stages';
            player.game = null;
            break;
        case '/api/retry-stage':
            if (player.difficulty) beginLevel(player.difficulty);
            break;
        case '/api/guess': {
            const game = player.game;
            if (!game || game.status !== 'playing') break;
            if (!game.choices.some((choice) => choice.letter === payload.choice)) break;
            game.selected_choice = payload.choice;
            if (payload.choice === game.correct_choice) {
                game.status = 'won';
                game.message = `ถูกต้อง! คำตอบคือ ${game.answer.toUpperCase()} +20 คะแนน`;
                player.score += 20;
                if (!player.completed_stages.includes(player.stage)) player.completed_stages.push(player.stage);
                player.unlocked_stage = Math.min(10, Math.max(player.unlocked_stage, player.stage + 1));
            } else {
                game.status = 'lost';
                game.message = `คำตอบที่ถูกคือ ${game.answer.toUpperCase()}`;
            }
            break;
        }
        case '/api/hint': {
            const game = player.game;
            if (game && game.status === 'playing' && game.revealed_hints < game.all_hints.length) {
                game.revealed_hints += 1;
                game.hints = game.all_hints.slice(0, game.revealed_hints);
                game.hints_remaining = game.all_hints.length - game.revealed_hints;
                game.message = 'เปิดคำใบ้เพิ่มแล้ว หัก 5 คะแนน';
                player.score = Math.max(0, player.score - 5);
            }
            break;
        }
        default:
            throw new Error('ไม่รู้จักคำสั่งนี้');
    }
    return buildViewState();
}

async function loadState() {
    const response = await fetch(new URL('static/questions.json', document.baseURI));
    if (!response.ok) throw new Error('โหลดคลังคำถามไม่สำเร็จ');
    questionBanks = (await response.json()).difficulties;
    try {
        const saved = JSON.parse(localStorage.getItem('byte-buddy-pages-v1'));
        player = saved && saved.seen_questions && saved.game !== undefined ? saved : makeNewPlayer();
        player.stage_difficulties ||= {};
    } catch {
        player = makeNewPlayer();
    }
    render(buildViewState());
}

function showScreen(name) {
    for (const [screenName, element] of Object.entries(screenElements)) {
        element.hidden = screenName !== name;
    }
    document.querySelector('#top-player').hidden = name === 'welcome';
    document.querySelector('#score-box').hidden = name === 'welcome';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function render(state) {
    const previousStatus = currentState?.status;
    currentState = state;
    document.querySelector('#player-name').textContent = state.player_name;
    document.querySelector('#stage-player-name').textContent = state.player_name ? `· ${state.player_name}` : '';
    document.querySelector('#score').textContent = state.score;
    document.querySelector('#completed-count').textContent = state.completed_stages.length;
    document.querySelector('#total-stage-count').textContent = state.total_stages;

    if (state.screen === 'stages') renderStages(state);
    if (state.screen === 'difficulty') renderDifficulties(state);
    if (state.screen === 'playing') {
        renderGame(state);
        if (previousStatus === 'playing' && state.status === 'won') showToast('ผ่านด่านแล้ว! เก่งมาก');
        if (previousStatus === 'playing' && state.status === 'lost') showToast('หมดโอกาสแล้ว ลองใหม่ได้นะ');
    }
    showScreen(state.screen);
    savePlayer();
}

function renderStages(state) {
    const grid = document.querySelector('#stage-grid');
    grid.replaceChildren(...Array.from({ length: state.total_stages }, (_, index) => {
        const stage = index + 1;
        const completed = state.completed_stages.includes(stage);
        const unlocked = stage <= state.unlocked_stage;
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `stage-card${!unlocked ? ' is-locked' : ''}${stage === state.unlocked_stage && !completed ? ' is-current' : ''}${completed ? ' is-completed' : ''}`;
        button.disabled = !unlocked;
        button.setAttribute('aria-label', `ด่าน ${stage}${completed ? ' ผ่านแล้ว' : unlocked ? '' : ' ยังไม่ปลดล็อก'}`);
        const stageName = ['เริ่มต้น', 'อุปกรณ์', 'ข้อมูล', 'ระบบ', 'เครือข่าย', 'โค้ด', 'ความปลอดภัย', 'ฮาร์ดแวร์', 'ดิจิทัล', 'บอสใหญ่'][index];
        button.innerHTML = `<span class="stage-number">${String(stage).padStart(2, '0')}</span><span class="stage-name">${stageName}</span><span class="stage-state">${completed ? 'complete' : unlocked ? 'พร้อมเล่น' : 'ล็อกอยู่'}</span>`;
        if (unlocked) button.addEventListener('click', () => selectStage(stage));
        return button;
    }));
}

function renderDifficulties(state) {
    document.querySelector('#selected-stage-number').textContent = String(state.selected_stage).padStart(2, '0');
    const grid = document.querySelector('#difficulty-grid');
    const icons = { easy: '01', medium: '02', hard: '03' };
    const labels = { easy: 'WARM UP', medium: 'LEVEL UP', hard: 'FINAL BOSS' };
    grid.replaceChildren(...difficultyOrder.map((key) => {
        const info = state.difficulties[key];
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'difficulty-card';
        button.dataset.difficulty = key;
        button.innerHTML = `<span class="difficulty-icon">${icons[key]}</span><span class="difficulty-level">${labels[key]}</span><h2>${info.label}</h2><p>${info.description}</p><span class="difficulty-count">${state.difficulty_counts[key]} คำถาม</span><span class="difficulty-arrow" aria-hidden="true">↗</span>`;
        button.addEventListener('click', () => startLevel(key));
        return button;
    }));
}

function renderChoices(state) {
    answerOptions.replaceChildren(...state.choices.map((choice) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'answer-option';
        button.disabled = state.status !== 'playing';
        button.setAttribute('aria-label', `ตัวเลือก ${choice.letter}: ${choice.text}`);
        const marker = document.createElement('span');
        marker.className = 'option-letter';
        marker.textContent = choice.letter;
        const text = document.createElement('span');
        text.className = 'option-text';
        text.textContent = choice.text;
        const indicator = document.createElement('span');
        indicator.className = 'option-indicator';
        indicator.setAttribute('aria-hidden', 'true');
        button.append(marker, text, indicator);

        if (state.status !== 'playing' && choice.letter === state.correct_choice) {
            button.classList.add('is-correct');
            indicator.textContent = '✓';
        } else if (choice.letter === state.selected_choice) {
            button.classList.add('is-incorrect');
            indicator.textContent = '×';
        } else {
            indicator.textContent = '↗';
        }
        button.addEventListener('click', () => submitChoice(choice.letter));
        return button;
    }));
}

function renderGame(state) {
    document.querySelector('#score').textContent = state.score;
    document.querySelector('#play-stage').textContent = `STAGE ${String(state.selected_stage).padStart(2, '0')} · ${state.difficulties[state.difficulty].label}`;
    document.querySelector('#category').textContent = state.category;
    document.querySelector('#question-number').textContent = `QUESTION ${String(state.round).padStart(2, '0')}`;
    document.querySelector('#question').textContent = state.question;
    document.querySelector('#clue-text').textContent = state.clue;
    document.querySelector('#extra-hints').replaceChildren(...state.hints.map((hint) => {
        const clue = document.createElement('p');
        clue.className = 'extra-hint';
        clue.textContent = hint;
        return clue;
    }));

    renderChoices(state);
    feedback.textContent = state.message;
    feedback.classList.toggle('is-success', state.status === 'won' || state.message.includes('ถูกต้อง'));
    feedback.classList.toggle('is-error', state.status === 'lost');
    hintButton.disabled = state.status !== 'playing' || state.hints_remaining === 0;
    hintButton.innerHTML = state.hints_remaining === 0
        ? '<span aria-hidden="true">✓</span> เปิดคำใบ้ครบแล้ว'
        : `<span aria-hidden="true">＋</span> ขอคำใบ้เพิ่ม <span class="hint-cost">−5 pts · ${state.hints_remaining} เหลือ</span>`;
    const result = document.querySelector('#round-result');
    const nextStage = document.querySelector('#next-stage-button');
    const tryAgain = document.querySelector('#try-again-button');
    result.hidden = state.status === 'playing';
    result.textContent = state.status === 'won'
        ? state.selected_stage === state.total_stages ? 'พิชิตครบทุกด่านแล้ว! สุดยอดไปเลย' : `ปลดล็อกด่าน ${String(state.unlocked_stage).padStart(2, '0')} แล้ว!`
        : state.status === 'lost' ? `คำตอบคือ ${state.answer}` : '';
    result.classList.toggle('is-lost', state.status === 'lost');
    nextStage.hidden = state.status !== 'won';
    nextStage.innerHTML = state.selected_stage === state.total_stages
        ? 'กลับไปดูแผนที่ <span aria-hidden="true">→</span>'
        : 'ไปด่านถัดไป <span aria-hidden="true">→</span>';
    tryAgain.hidden = state.status !== 'lost';
}

async function submitChoice(choice) {
    if (!choice || !currentState || currentState.status !== 'playing') return;
    try {
        render(await requestJson('/api/guess', { choice }));
    } catch (error) {
        feedback.textContent = error.message;
        feedback.classList.add('is-error');
    }
}

async function selectStage(stage) {
    try {
        render(await requestJson('/api/select-stage', { stage }));
    } catch (error) {
        showToast(error.message);
    }
}

async function startLevel(difficulty) {
    try {
        render(await requestJson('/api/start-level', { difficulty }));
    } catch (error) {
        showToast(error.message);
    }
}

function showToast(message) {
    const toast = document.querySelector('#toast');
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast.classList.remove('is-visible'), 1900);
}

document.querySelector('#open-name-dialog').addEventListener('click', () => {
    nameError.textContent = '';
    nameDialog.showModal();
    nameInput.focus();
});

document.querySelector('#name-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const name = nameInput.value.trim();
    if (!name) {
        nameError.textContent = 'ใส่ชื่อก่อนออกผจญภัยนะ';
        nameInput.focus();
        return;
    }
    try {
        render(await requestJson('/api/start', { name }));
        nameDialog.close();
    } catch (error) {
        nameError.textContent = error.message;
    }
});

document.querySelector('#back-to-stages').addEventListener('click', async () => {
    try { render(await requestJson('/api/return-to-stages')); } catch (error) { showToast(error.message); }
});

document.querySelector('#back-to-difficulty').addEventListener('click', async () => {
    try { render(await requestJson('/api/return-to-stages')); } catch (error) { showToast(error.message); }
});

document.querySelector('#reset-player').addEventListener('click', () => {
    nameInput.value = '';
    nameDialog.showModal();
    nameInput.focus();
});

document.querySelector('#next-stage-button').addEventListener('click', async () => {
    if (currentState.selected_stage === currentState.total_stages) {
        try { render(await requestJson('/api/return-to-stages')); } catch (error) { showToast(error.message); }
        return;
    }
    await selectStage(currentState.selected_stage + 1);
});

document.querySelector('#try-again-button').addEventListener('click', async () => {
    try { render(await requestJson('/api/retry-stage')); } catch (error) { showToast(error.message); }
});

hintButton.addEventListener('click', async () => {
    try { render(await requestJson('/api/hint')); } catch (error) { showToast(error.message); }
});

loadState().catch((error) => showToast(error.message));