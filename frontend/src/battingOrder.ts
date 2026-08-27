import type { Player } from './types'

export function isValidOrder(order: (Player | null)[]): boolean {
  return order.every((p, i) => p !== null && p.position_min <= i + 1 && i + 1 <= p.position_max)
}

/**
 * Online bipartite matching: try to slot `candidate` into `assignment`
 * (an 11-length array of already-placed players) without removing anyone,
 * only relocating existing players to other slots within their own range
 * (a standard augmenting path). Returns the new assignment if a slot could
 * be found for everyone, or null if adding this candidate would make the
 * batting order impossible to complete - this is what must gate whether a
 * player can be picked at all, not just a check run after all 11 are in.
 */
export function tryAugment(assignment: (Player | null)[], candidate: Player): (Player | null)[] | null {
  const n = assignment.length
  const work = [...assignment]

  function augment(player: Player, visited: Set<number>): boolean {
    const hi = Math.min(player.position_max, n)
    for (let slot = player.position_min - 1; slot < hi; slot++) {
      if (visited.has(slot)) continue
      visited.add(slot)
      const occupant = work[slot]
      if (occupant === null || augment(occupant, visited)) {
        work[slot] = player
        return true
      }
    }
    return false
  }

  return augment(candidate, new Set()) ? work : null
}
