class CardAnalyzer:
    @staticmethod
    def find_cards_with_shared_factions(deck, card_name):
        target_card = next((card for card in deck.cards if card.name == card_name), None)
        if not target_card:
            print(f"Card '{card_name}' not found in the deck!")
            return

        matching_cards = []
        for card in deck.cards:
            if card == target_card:
                continue
            shared_factions = target_card.faction_ids & card.faction_ids
            if shared_factions:
                matching_cards.append((card, len(shared_factions)))

        matching_cards.sort(key=lambda x: x[1], reverse=True)

        if matching_cards:
            print(f"Cards with shared factions with '{target_card.name}':")
            for card, shared_count in matching_cards:
                print(f"{card.name} - Shared factions: {shared_count}")
        else:
            print(f"'{target_card.name}' has unique factions.") 