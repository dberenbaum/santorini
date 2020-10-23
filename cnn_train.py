import click
import torch

import cnn
import factory


@click.command()
@click.option("--iters", "-i", type=int, default=1000)
@click.option("--n", "-n", type=int, default=50000)
@click.option("--epochs", "-e", "epochs", type=int, default=100)
@click.option("--db", "db", default="cnn")
@click.option("--model_path", "-p", "model_path", default=cnn.MODEL_PATH)
@click.option("--printn", "printn", type=int, default=10)
def main(iters, n, epochs, db, model_path, printn=100):
    for i in range(iters):
        try:
            model = cnn.load_model(model_path)
        except FileNotFoundError:
            print(f"No file found at {model_path}.")
            model = cnn.ValueNet()
        print("Get samples")
        with factory.serializer_factory.get_serializer("mongo_bulk", db=db) as tree:
            samples = cnn.get_samples(tree, n=n)
        print("Convert to torch")
        x, y, w = cnn.samples_to_torch(samples)
        print("Train model")
        for epoch in range(epochs):
            y_pred, loss = cnn.train_epoch(model, x, y, w)
            if not epoch % printn:
                print(epoch, loss.item())
        torch.save(model.state_dict(), model_path)


if __name__ == '__main__':
    main()
