import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Button, Grid, Icon, Typography } from "@material-ui/core";

export default function VertexList({ vertices }) {
  return (
    <Grid container>
      <Grid item xs={12}>
        <Typography variant="h6">Vertices</Typography>
      </Grid>
      <Grid item xs={12}>
        <Button
          variant="contained"
          color="primary"
          href="/vertex/new"
          endIcon={<Icon>add</Icon>}
        >
          Add
        </Button>
      </Grid>
      <Grid item xs={12}>
        <List>
          {vertices.map((d, i) => (
            <ListItem key={d.id} divider={i < vertices.length - 1}>
              <ListItemText primary={d.name} />
            </ListItem>
          ))}
        </List>
      </Grid>
    </Grid>
  );
}

export async function getServerSideProps(context) {
  const res = await fetch("http://rest:3000/vertex");
  const vertices = await res.json();

  return {
    props: {
      vertices,
    },
  };
}
