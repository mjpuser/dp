import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";

export default function About({ datasets }) {
  return (
    <>
      Datasets
      <List>
        {datasets.map((d) => (
          <ListItem key={d.id}>
            <ListItemText primary={d.name} />
          </ListItem>
        ))}
      </List>
    </>
  );
}

export async function getServerSideProps(context) {
  const res = await fetch("http://rest:3000/dataset");
  const datasets = await res.json();

  return {
    props: {
      datasets,
    },
  };
}
