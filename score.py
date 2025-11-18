
    
def calculer(reference:list[int], essai:list[int], score:int=0)->int:
    """IN: 2 listes de 0 ou 1 (0 = silence, 1 = bruit)
       OUT: un score
    """
    assert len(reference) <= len(essai)
    if len(reference) == len(essai) == 0:
        return score
    if reference[0] == 1:
        if essai[0] == 1:
            score += 10
            return calculer(reference[1:], essai[1:], score)
        if len(essai) > 1:
            if essai[1] == 1:
                score += 5
                essai = [0] + essai[2:]
                if reference[1] == 1:
                    essai[0] = 1
                return calculer(reference[1:], essai, score)
    if reference[0] == 0:
        if essai[0] == 1:
            score -= 10
            return calculer(reference[1:], essai[1:], score)
    return calculer(reference[1:], essai[1:], score)

def calculerPourcentage(reference:list[int],essai:list[int])->float:
    """ Calcule le pourcentage obtenu.
    """
    return max(0,calculer(reference, essai) / calculer(reference,reference)) * 100

#print(calculerPourcentage([0,0,0,0,0,1,0],
#                          [0,0,0,0,0,0,1]))