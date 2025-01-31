# card.py

from factions import FACTIONS

class Card:
    def __init__(self, name, rank):
        self.name = name
        self.rank = rank
        self.faction_ids = set()

    def add_faction(self, faction_id):
        """Add faction to the card by its ID."""
        if faction_id in FACTIONS:
            self.faction_ids.add(faction_id)
        else:
            print(f"Faction with ID '{faction_id}' does not exist.")

    def remove_faction(self, faction_id):
        """Remove faction from the card by its ID."""
        if faction_id in self.faction_ids:
            self.faction_ids.remove(faction_id)
        else:
            print(f"Faction with ID '{faction_id}' not found in card '{self.name}'.")

    def has_faction(self, faction_id):
        """Check if the card belongs to the specified faction by its ID."""
        return faction_id in self.faction_ids

    def __str__(self):
        factions_str = ', '.join(FACTIONS[fid] for fid in self.faction_ids) if self.faction_ids else 'none'
        return f"Card: {self.name}, Rank: {self.rank}, Factions: {factions_str}"

    def name_only(self):
        """Display only the name of the card, for use on the table."""
        return self.name
    # def get_active_factions(self, active_factions):
    #     """Determine active factions based on the current active factions."""
    #     if not active_factions:
    #         return self.faction_ids
    #     return self.faction_ids.intersection(active_factions)