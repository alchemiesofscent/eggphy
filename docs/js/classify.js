// Shared classification logic for witnesses/recipes across pages
// Exposes window.classifyRecipe(obj)
(function(){
  function classify(obj) {
    try {
      const id = obj && obj.metadata && obj.metadata.witness_id;
      const ingredients = obj && obj.ingredients && obj.ingredients.diagnostic_variants;
      const process = obj && obj.process_steps && obj.process_steps.critical_variants;

      if (!id || !ingredients || !process) return 'E_Meta';

      // Outliers and unique branches
      if (['W23','W27','W37','W74','W87'].includes(id)) return 'E_Meta';
      if (process.boiling_timing === 'before_writing') return 'F_Anomalous';
      if (id === 'W57') return 'G_Cepak';

      // Salt-water-boil detection
      const hasSaltWaterBoil = !!(obj && obj.process_steps && Array.isArray(obj.process_steps.preparation_sequence) &&
        obj.process_steps.preparation_sequence.some(s => s && s.details && (
          s.details.toLowerCase().includes('salt water') || s.details.toLowerCase().includes('salzwasser')
        )));

      if (ingredients.gall_presence === 'present' && process.soaking_duration !== 'days' && hasSaltWaterBoil) {
        return 'D_SaltWaterBoil';
      }
      if (ingredients.gall_presence === 'absent' && process.soaking_duration === 'days') {
        return 'B_LongSoak';
      }
      if (ingredients.gall_presence === 'absent' && process.soaking_duration !== 'days') {
        return 'C_Modern';
      }
      if (ingredients.gall_presence === 'present') {
        return 'A_Classical';
      }

      return 'E_Meta';
    } catch (_) {
      return 'E_Meta';
    }
  }

  window._classifyRecipe = classify;
})();
