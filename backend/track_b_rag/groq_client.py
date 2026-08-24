from backend.config import GROQ_API_KEY

def answer_with_groq(query, context_chunks):
    """If GROQ_API_KEY present, this function would call Groq API. Otherwise return a simple grounded answer."""
    if GROQ_API_KEY:
        try:
            import groq
            client = groq.Client(api_key=GROQ_API_KEY)
            # This is a placeholder; actual call depends on groq SDK
            prompt = 'Context:\n' + '\n---\n'.join(context_chunks) + f"\n\nQuestion: {query}\nAnswer:"
            resp = client.completions.create(model='mixtral', prompt=prompt, max_tokens=256)
            return {'answer': resp.choices[0].text, 'raw': resp}
        except Exception as e:
            print('Groq call failed:', e)

    # Fallback: return concatenated context as the answer with simple highlighting
    answer = 'Grounded answer (fallback):\n' + '\n'.join(context_chunks[:3])
    return {'answer': answer}


if __name__ == '__main__':
    print(answer_with_groq('Which vendor has the best warranty?', ['Warranty: 24 months\nVendor: X', 'Warranty: 12 months\nVendor: Y']))
