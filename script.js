document.addEventListener('DOMContentLoaded', () => {
  const mockPapers = [
    {
      id: 1,
      title: 'Attention Is All You Need',
      abstract: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder architecture. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.',
      pdfUrl: 'https://arxiv.pdf/1706.03762.pdf' // Example ArXiv PDF
    },
    {
      id: 2,
      title: 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
      abstract: 'We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial task-specific architecture modifications. BERT is conceptually simple and empirically powerful. It obtains new state-of-the-art results on eleven natural language processing tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement), SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement) and SQuAD v2.0 Test F1 to 83.1 (5.1 point absolute improvement).',
      pdfUrl: 'https://arxiv.pdf/1810.04805.pdf' // Example ArXiv PDF
    },
    {
      id: 3,
      title: 'Generative Adversarial Networks',
      abstract: 'We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G. The training procedure for G is to maximize the probability of D making a mistake. This framework corresponds to a minimax two-player game. In the space of arbitrary functions G and D, a unique solution exists, with G recovering the training data distribution and D equal to 1/2 everywhere. In the case where G and D are defined by multilayer perceptrons, the entire system can be trained with backpropagation. There is no need for any Markov chains or unrolled approximate inference networks during either training or generation of samples. Experiments demonstrate the potential of the framework through qualitative and quantitative evaluation of the generated samples.',
      pdfUrl: 'https://arxiv.pdf/1406.2661.pdf' // Example ArXiv PDF
    }
  ];

  const paperListUl = document.querySelector('#paper-list ul');
  const paperDetailsDiv = document.getElementById('paper-details');
  const selectedPaperTitleDiv = document.getElementById('selected-paper-title');
  const selectedPaperAbstractDiv = document.getElementById('selected-paper-abstract');
  const pdfPreviewDiv = document.getElementById('selected-paper-pdf-preview');
  const initialPdfMessage = pdfPreviewDiv.querySelector('p');

  function displayPaperDetails(paper) {
    selectedPaperTitleDiv.textContent = paper.title;
    selectedPaperAbstractDiv.textContent = paper.abstract;

    // Handle PDF preview
    if (initialPdfMessage) {
        initialPdfMessage.style.display = 'none'; // Hide the initial message
    }

    let iframe = pdfPreviewDiv.querySelector('iframe');
    if (iframe) {
      iframe.src = paper.pdfUrl;
    } else {
      iframe = document.createElement('iframe');
      iframe.src = paper.pdfUrl;
      iframe.width = '100%';
      iframe.height = '100%'; // Will be constrained by parent's height in CSS
      pdfPreviewDiv.appendChild(iframe);
    }

    paperDetailsDiv.classList.remove('hidden');
    paperDetailsDiv.classList.add('visible');
  }

  function populatePaperList() {
    if (!paperListUl) {
      console.error('Paper list UL element not found!');
      return;
    }
    paperListUl.innerHTML = ''; // Clear existing list items

    mockPapers.forEach(paper => {
      const listItem = document.createElement('li');
      listItem.textContent = paper.title;
      listItem.dataset.paperId = paper.id; // Optional: store paper ID
      listItem.addEventListener('click', () => displayPaperDetails(paper));
      paperListUl.appendChild(listItem);
    });
  }

  // Initial population of the paper list
  populatePaperList();
});
