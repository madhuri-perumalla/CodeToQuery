export const formatCost = (cost: number): string => {
  if (cost >= 1000000) {
    return `${(cost / 1000000).toFixed(2)}M`;
  }
  if (cost >= 1000) {
    return `${(cost / 1000).toFixed(2)}K`;
  }
  return cost.toFixed(2);
};
