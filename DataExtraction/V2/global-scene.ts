import type { BattleScene } from "#app/battle-scene";

export let globalScene: BattleScene;

export function initGlobalScene(scene: BattleScene): void {
  globalScene = scene;
  window.globalScene = globalScene;

  function serializePartyPokemon(p) {
  return {
    formIndex: p.formIndex,
    dex_nr: p.species?.speciesId,
    hp: p.hp,
    stats: p.stats,
    visible: p._visible,
    moveset: p.moveset?.map(m => ({
      id: m.moveId,
    })),
  };
}

  function serializeEnemyPokemon(p) {
  return {
    formIndex: p.formIndex,
    dex_nr: p.species?.speciesId,
    hp: p.hp,
    stats: p.stats,
  };
}


globalThis.__GLOBAL_SCENE_DATA__ = () => ({
  player: scene.party.map(serializePartyPokemon),
  enemy: scene.currentBattle.enemyParty.map(serializeEnemyPokemon)
  //phase: scene.phaseManager
});

  // Aktionen vom Python-Agenten
  //globalThis.__GLOBAL_SCENE_ACTION__ = (action: string) => {
  //  switch(action) {
  //    case "w": scene.inputController.gamepadButtonDown("w"); scene.inputController.gamepadButtonUp("w"); break;
  //    case 'w': scene.inputController.simulateKey('w'); break;
  //    case 'a': scene.inputController.simulateKey('a'); break;
  //    case 's': scene.inputController.simulateKey('s'); break;
  //    case 'd': scene.inputController.simulateKey('d'); break;
  //    case 'space': scene.inputController.simulateKey(' '); break;
  //  }
  //};
}
