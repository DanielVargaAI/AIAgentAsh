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
      level: p.level,
      luck: p.luck,
      isTerastallized: p.isTerastallized,
      nature: p.nature,
      passive: p.passive,
      abilityIndex: p.abilityIndex,
      gender: p.gender,
      ivs: p.ivs,
      teraType: p.teraType,
    };
  }

  function serializeEnemyPokemon(p) {
    return {
      formIndex: p.formIndex,
      dex_nr: p.species?.speciesId,
      hp: p.hp,
      stats: p.stats,
      luck: p.luck,
    };
  }

  globalThis.__GLOBAL_SCENE_DATA__ = () => ({
    player: scene.party.map(serializePartyPokemon),
    enemy: scene.currentBattle.enemyParty.map(serializeEnemyPokemon)
    phase: scene.phaseManager.currentPhase.phaseName
  });
}
